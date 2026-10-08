"""Score saved predictions against what actually happened, Gameweek by Gameweek."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy import stats

from ..data.normalize import load_historical_player_gw
from ..optimization.lineup import pick_squad
from ..optimization.simulate import score_squad
from ..utils.config import load_config

# name shown in the track record -> column in the prediction snapshot
PREDICTORS = {
    "model": "expected_points",
    "fpl_ep_next": "fpl_ep_next",
    "form_5gw": "form_5gw",
    "last_gw": "last_gw_points",
}
METRICS = ["mae", "spearman", "top10_points", "captain_points", "xi_points"]


def _snapshot_dir(config: dict) -> Path:
    return Path(config.get("predictions", {}).get("path", "data/predictions"))


def _score(snapshot: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
    rows = []
    for name, column in PREDICTORS.items():
        pool = snapshot.assign(pred=snapshot[column].astype(float).fillna(0.0))
        ranked = pool.sort_values("pred", ascending=False, kind="stable")
        squad = pick_squad(pool, "pred")
        informative = pool["pred"].nunique() > 1 and pool["next_gw_points"].nunique() > 1
        rows.append(
            {
                "predictor": name,
                "mae": float((pool["pred"] - pool["next_gw_points"]).abs().mean()),
                "spearman": float(stats.spearmanr(pool["pred"], pool["next_gw_points"])[0])
                if informative
                else float("nan"),
                "top10_points": float(ranked["next_gw_points"].head(top_k).mean()),
                "captain_points": float(ranked["next_gw_points"].iloc[0]),
                "xi_points": score_squad(squad),
                "players": len(pool),
            }
        )
    return pd.DataFrame(rows)


def score_gameweek(
    season: str | None = None,
    gameweek: int | None = None,
    config_path: str = "configs/config.yaml",
) -> pd.DataFrame:
    """Compare the saved pre-deadline snapshot of a Gameweek with real results.

    Needs fresh results (``fetch_live.py``) after the Gameweek has been played.
    Appends to ``track_record.csv`` (replacing any earlier score of that Gameweek).
    """
    config = load_config(config_path)
    season = season or config["data"]["seasons"][-1]
    raw = Path(config["data"]["raw_path"]) / season
    results = load_historical_player_gw(raw / "merged_gw.csv", season, raw / "teams.csv")
    if gameweek is None:
        gameweek = int(results["gameweek"].max())

    snapshot_path = _snapshot_dir(config) / f"{season}_gw{gameweek}.csv"
    if not snapshot_path.exists():
        raise FileNotFoundError(
            f"No saved prediction for {season} GW{gameweek} ({snapshot_path}). "
            "Predictions can only be scored if they were made before the deadline."
        )
    actual = (
        results[results["gameweek"] == gameweek]
        .groupby("player_id")["total_points"]
        .sum()
        .rename("next_gw_points")
    )
    snapshot = pd.read_csv(snapshot_path).merge(actual, left_on="player_id", right_index=True)
    snapshot = snapshot[snapshot["prior_gws"] >= config["evaluation"].get("min_history", 3)]
    if snapshot.empty:
        raise ValueError(f"No results found for {season} GW{gameweek} yet.")

    scored = _score(snapshot, config["evaluation"].get("top_k", 10)).assign(
        season=season, gameweek=gameweek
    )
    path = _snapshot_dir(config) / "track_record.csv"
    if path.exists():
        old = pd.read_csv(path)
        old = old[~((old["season"] == season) & (old["gameweek"] == gameweek))]
        scored = pd.concat([old, scored], ignore_index=True)
    scored = scored.sort_values(["season", "gameweek", "predictor"])
    scored.to_csv(path, index=False)
    return scored[(scored["season"] == season) & (scored["gameweek"] == gameweek)]


def load_track_record(config: dict, season: str) -> pd.DataFrame:
    path = _snapshot_dir(config) / "track_record.csv"
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    return frame[frame["season"] == season]


def track_summary(record: pd.DataFrame) -> dict | None:
    """Average of each predictor over all scored Gameweeks (for the dashboard)."""
    if record.empty:
        return None
    order = list(PREDICTORS)
    means = record.groupby("predictor")[METRICS].mean().reindex(order).dropna(how="all")
    return {
        "gameweeks": sorted(int(g) for g in record["gameweek"].unique()),
        "rows": [
            {"predictor": name, **row} for name, row in means.round(3).to_dict("index").items()
        ],
    }
