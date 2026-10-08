from __future__ import annotations

import pandas as pd

from .fixture_features import add_fixture_context

TARGET = "next_gw_points"
POSITION_CODES = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3}

# stat column -> short prefix used in feature names
ROLL_STATS = {
    "total_points": "pts",
    "minutes": "min",
    "bps": "bps",
    "ict_index": "ict",
    "xgi": "xgi",
}


def rolling_mean(
    frame: pd.DataFrame,
    value_column: str,
    window: int,
    group_column: str = "player_id",
) -> pd.Series:
    """Calculate a historical rolling mean using only prior observations."""
    if window < 1:
        raise ValueError("window must be >= 1")

    return frame.groupby(group_column)[value_column].transform(
        lambda series: series.shift(1).rolling(window, min_periods=1).mean()
    )


def feature_columns(windows: tuple[int, ...] = (3, 5, 10), form_window: int = 5) -> list[str]:
    """Names of the model input columns produced by :func:`build_model_table`."""
    columns = [f"{prefix}_roll{w}" for prefix in ROLL_STATS.values() for w in windows]
    columns += [
        "pts_last",
        "min_last",
        "pts_season_mean",
        "prior_gws",
        "pos_code",
        "value",
        "selected",
        "is_home",
        "n_fixtures",
        f"team_gf_roll{form_window}",
        f"team_ga_roll{form_window}",
        f"opp_gf_roll{form_window}",
        f"opp_ga_roll{form_window}",
    ]
    return columns


def _player_keys(frame: pd.DataFrame) -> pd.Series:
    """Stable cross-season player key (FPL ids reset every season).

    Name+position identifies a player across seasons; if that is ambiguous
    inside one season the season-local player_id is appended.
    """
    key = frame["name"].astype("string").str.strip() + "|" + frame["position"].astype("string")
    ids_per_key = frame.groupby(["season", key])["player_id"].transform("nunique")
    ambiguous = ids_per_key > 1
    return key.where(~ambiguous, key + "#" + frame["player_id"].astype("string"))


def build_model_table(
    player_gw: pd.DataFrame,
    windows: tuple[int, ...] = (3, 5, 10),
    form_window: int = 5,
) -> pd.DataFrame:
    """Turn canonical player/fixture rows into a leakage-free modelling table.

    One output row = one player in one Gameweek. Every feature uses only data
    from earlier Gameweeks (or information fixed before kick-off such as
    venue, price and opponent). ``next_gw_points`` is what the player then
    scored in that Gameweek.
    """
    df = add_fixture_context(player_gw.copy(), form_window)
    df["xgi"] = df["xgi"].astype("float64")
    df["ict_index"] = df["ict_index"].astype("float64")
    df["player_key"] = _player_keys(df)

    seasons = sorted(df["season"].unique())
    df["season_order"] = df["season"].map({s: i for i, s in enumerate(seasons)})
    df["is_home"] = df["was_home"].astype("float64")

    form_cols = [
        f"{side}_{kind}_roll{form_window}" for side in ("team", "opp") for kind in ("gf", "ga")
    ]
    group = ["season", "season_order", "gameweek", "player_key"]

    sums = df.groupby(group)[list(ROLL_STATS)].sum(min_count=1)  # keep NaN xG for old seasons
    means = df.groupby(group)[["is_home", "selected", *form_cols]].mean()
    other = df.groupby(group).agg(
        name=("name", "first"),
        player_id=("player_id", "first"),
        team_id=("team_id", "first"),
        position=("position", "first"),
        value=("value", "max"),
        n_fixtures=("fixture_id", "nunique"),
    )
    table = pd.concat([sums, means, other], axis=1).reset_index()

    # Global chronological index (works across seasons).
    order = (
        table[["season_order", "gameweek"]]
        .drop_duplicates()
        .sort_values(["season_order", "gameweek"])
        .reset_index(drop=True)
    )
    order["time_idx"] = range(len(order))
    table = table.merge(order, on=["season_order", "gameweek"], how="left")
    table = table.sort_values(["player_key", "time_idx"]).reset_index(drop=True)

    for stat, prefix in ROLL_STATS.items():
        for w in windows:
            table[f"{prefix}_roll{w}"] = rolling_mean(table, stat, w, "player_key")
    table["pts_last"] = table.groupby("player_key")["total_points"].shift(1)
    table["min_last"] = table.groupby("player_key")["minutes"].shift(1)
    table["pts_season_mean"] = table.groupby(["player_key", "season"])["total_points"].transform(
        lambda s: s.shift(1).expanding().mean()
    )
    table["prior_gws"] = table.groupby("player_key").cumcount()
    table["pos_code"] = table["position"].map(POSITION_CODES)
    table[TARGET] = table["total_points"]
    table["actual_minutes"] = table["minutes"]  # kept for analysis only, never a feature

    return table.sort_values(["time_idx", "player_key"]).reset_index(drop=True)
