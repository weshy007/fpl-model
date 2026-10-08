from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from ..dashboard import render_dashboard
from ..data.normalize import load_historical_player_gw
from ..data.upcoming import availability_factor, build_upcoming_rows, next_gameweek
from ..features.player_features import TARGET, build_model_table, feature_columns
from ..models.points import PointsPredictor, make_estimator
from ..optimization.lineup import pick_squad
from ..utils.config import load_config
from .ingestion import load_player_gw

log = logging.getLogger(__name__)


def _opponent_labels(rows: pd.DataFrame, short_names: dict[int, str]) -> pd.Series:
    """Text such as ``BOU (H)`` (comma-joined for double Gameweeks) per player id."""
    label = rows["opponent_team_id"].map(short_names).fillna("?") + rows["was_home"].map(
        {True: " (H)", False: " (A)"}
    )
    return label.groupby(rows["player_id"]).agg(", ".join)


def run(
    season: str | None = None,
    gameweek: int | None = None,
    config_path: str = "configs/config.yaml",
    note: str | None = None,
) -> dict:
    """Predict every player's points for an upcoming Gameweek.

    Reads ``data/raw/<season>/`` (``fetch_live.py`` or the community dataset),
    trains on every completed Gameweek before the target one, and writes a CSV
    plus a self-contained HTML dashboard.
    """
    config = load_config(config_path)
    seasons = config["data"]["seasons"]
    season = season or seasons[-1]
    raw = Path(config["data"]["raw_path"]) / season

    players = pd.read_csv(raw / "players_raw.csv")
    teams = pd.read_csv(raw / "teams.csv")
    fixtures = pd.read_csv(raw / "fixtures.csv")
    gameweek = gameweek or next_gameweek(fixtures)
    total_file = raw / "total_players.txt"
    total_players = (
        float(total_file.read_text() or 10_000_000) if total_file.exists() else 10_000_000
    )

    # History: prior seasons from processed tables, current season straight from raw.
    prior = [s for s in seasons if s < season]
    history = [load_player_gw(prior, config["data"]["processed_path"])] if prior else []
    history_through = None
    if (raw / "merged_gw.csv").exists():
        current = load_historical_player_gw(raw / "merged_gw.csv", season, raw / "teams.csv")
        current = current[current["gameweek"] < gameweek]  # never use the target Gameweek
        if not current.empty:
            history_through = int(current["gameweek"].max())
            history.append(current)
    upcoming = build_upcoming_rows(players, fixtures, season, gameweek, total_players)
    if upcoming.empty:
        raise ValueError(f"No fixtures found for {season} GW{gameweek}")

    combined = pd.concat([*history, upcoming], ignore_index=True)
    table = build_model_table(
        combined,
        tuple(config["features"]["rolling_windows"]),
        config["features"]["form_window"],
    )
    features = feature_columns(
        tuple(config["features"]["rolling_windows"]), config["features"]["form_window"]
    )

    is_target = (table["season"] == season) & (table["gameweek"] == gameweek)
    train = table[~is_target & table[TARGET].notna()]
    target_rows = table[is_target].copy()
    log.info("Training on %s player-Gameweeks", f"{len(train):,}")
    model = make_estimator(config["model"].get("lightgbm"), config["model"]["random_seed"])
    model.fit(train[features], train[TARGET])
    target_rows["model_points"] = PointsPredictor(model).predict(target_rows[features])

    info = players.set_index("id")
    target_rows["web_name"] = target_rows["player_id"].map(info["web_name"])
    target_rows["status"] = target_rows["player_id"].map(info["status"])
    target_rows["news"] = target_rows["player_id"].map(info["news"]).fillna("")
    target_rows["chance"] = pd.to_numeric(
        target_rows["player_id"].map(info["chance_of_playing_next_round"]), errors="coerce"
    )
    factor = availability_factor(
        players.set_index("id").loc[target_rows["player_id"]].reset_index(drop=True)
    )
    target_rows["availability"] = factor.to_numpy()
    target_rows["expected_points"] = target_rows["model_points"] * target_rows["availability"]

    short = dict(zip(teams["id"], teams["short_name"]))
    target_rows["team"] = target_rows["team_id"].map(short)
    target_rows["opponent"] = target_rows["player_id"].map(_opponent_labels(upcoming, short))
    target_rows["price"] = target_rows["value"] / 10
    target_rows["form_5gw"] = target_rows["pts_roll5"]
    target_rows["last_gw_points"] = target_rows["pts_last"]

    columns = [
        "player_id", "name", "web_name", "team", "position", "opponent", "price",
        "expected_points", "model_points", "availability", "status", "chance", "news",
        "form_5gw", "last_gw_points", "n_fixtures", "prior_gws", "team_id", "value",
    ]  # fmt: skip
    predictions = (
        target_rows[columns]
        .sort_values("expected_points", ascending=False, kind="stable")
        .reset_index(drop=True)
    )
    squad = pick_squad(predictions, "expected_points")

    meta = {
        "season": season,
        "gameweek": gameweek,
        "history_through_gw": history_through,
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "train_rows": len(train),
        "note": note,
    }
    out = Path(config["dashboard"]["output_path"])
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{season}_gw{gameweek}"
    predictions.to_csv(out / f"{stem}_predictions.csv", index=False)
    html = render_dashboard(predictions, squad, meta)
    (out / f"{stem}.html").write_text(html, encoding="utf-8")
    (out / "latest.html").write_text(html, encoding="utf-8")
    log.info("Wrote %s", out / f"{stem}.html")
    return {"predictions": predictions, "squad": squad, "meta": meta, "path": out / f"{stem}.html"}
