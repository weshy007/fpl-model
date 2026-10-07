from __future__ import annotations

from pathlib import Path

import pandas as pd

from .schema import (
    PLAYER_GW_COLUMNS,
    SOURCE_ALIASES,
    VALID_POSITIONS,
)
from .validation import require_columns, validate_player_gw

POSITION_MAP = {
    1: "GK",
    2: "DEF",
    3: "MID",
    4: "FWD",
}

_INT_COLUMNS = (
    "gameweek",
    "player_id",
    "team_id",
    "fixture_id",
    "opponent_team_id",
    "minutes",
    "starts",
    "total_points",
    "goals_scored",
    "assists",
    "clean_sheets",
    "goals_conceded",
    "own_goals",
    "penalties_saved",
    "penalties_missed",
    "saves",
    "yellow_cards",
    "red_cards",
    "bonus",
    "bps",
    "selected",
    "transfers_balance",
    "transfers_in",
    "transfers_out",
    "value",
)

_FLOAT_COLUMNS = (
    "influence",
    "creativity",
    "threat",
    "ict_index",
    "xg",
    "xa",
    "xgi",
    "xgc",
)

_DEFAULT_ZERO_COLUMNS = (
    "starts",
    "goals_scored",
    "assists",
    "clean_sheets",
    "goals_conceded",
    "own_goals",
    "penalties_saved",
    "penalties_missed",
    "saves",
    "yellow_cards",
    "red_cards",
    "bonus",
    "bps",
    "selected",
    "transfers_balance",
    "transfers_in",
    "transfers_out",
)


def _first_existing(frame: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        if alias in frame.columns:
            return alias
    return None


def _position_series(frame: pd.DataFrame) -> pd.Series:
    source = _first_existing(frame, SOURCE_ALIASES["position"])
    if source is None:
        raise ValueError("Source is missing both 'position' and 'element_type'")

    values = frame[source]
    if pd.api.types.is_numeric_dtype(values):
        invalid_codes = sorted(set(values.dropna()) - set(POSITION_MAP))
        if invalid_codes:
            raise ValueError(f"Invalid source position values: {invalid_codes}")
        mapped = values.map(POSITION_MAP)
    else:
        mapped = values

    mapped = mapped.astype("string").str.upper().replace({"GOALKEEPER": "GK", "DEFENDER": "DEF", "MIDFIELDER": "MID", "FORWARD": "FWD"})

    invalid = sorted(set(mapped.dropna()) - VALID_POSITIONS)
    if invalid:
        raise ValueError(f"Invalid source position values: {invalid}")
    return mapped


def _numeric_series(frame: pd.DataFrame, canonical: str, *, required: bool) -> pd.Series:
    source = _first_existing(frame, SOURCE_ALIASES[canonical])
    if source is None:
        if required:
            raise ValueError(f"Source is missing required column for '{canonical}'")
        return pd.Series(pd.NA, index=frame.index, dtype="Float64")
    return pd.to_numeric(frame[source], errors="coerce")


def normalize_player_gw(frame: pd.DataFrame, season: str) -> pd.DataFrame:
    """Convert one raw merged-GW dataframe into the canonical player_gw schema.

    The output has exactly one row per player/Gameweek. Source-specific names
    are mapped here so feature code never needs to know the upstream schema.
    """
    require_columns(frame, ["name"])

    output = pd.DataFrame(index=frame.index)
    output["season"] = pd.Series(str(season), index=frame.index, dtype="string")
    output["gameweek"] = _numeric_series(frame, "gameweek", required=True)
    output["player_id"] = _numeric_series(frame, "player_id", required=True)
    output["name"] = frame["name"].astype("string").str.strip()
    output["team_id"] = _numeric_series(frame, "team_id", required=True)
    output["position"] = _position_series(frame)
    output["fixture_id"] = _numeric_series(frame, "fixture_id", required=True)
    output["opponent_team_id"] = _numeric_series(frame, "opponent_team_id", required=True)

    was_home_source = _first_existing(frame, ("was_home",))
    if was_home_source is None:
        raise ValueError("Source is missing required column 'was_home'")
    output["was_home"] = frame[was_home_source].astype("boolean")

    kickoff_source = _first_existing(frame, SOURCE_ALIASES["kickoff_time"])
    if kickoff_source:
        output["kickoff_time"] = (
            pd.to_datetime(frame[kickoff_source], errors="coerce", utc=True)
            .dt.tz_convert(None)
        )
    else:
        output["kickoff_time"] = pd.Series(
            pd.NaT, index=frame.index, dtype="datetime64[ns]"
        )

    for column in _INT_COLUMNS:
        if column in {"gameweek", "player_id", "team_id", "fixture_id", "opponent_team_id"}:
            continue
        output[column] = _numeric_series(frame, column, required=column == "minutes")

    for column in _FLOAT_COLUMNS:
        output[column] = _numeric_series(frame, column, required=False)

    # A missing event-level count means zero for match statistics in the FPL
    # source. Expected-stat fields remain NaN when that source did not provide
    # them; we never fabricate xG/xA for older seasons.
    for column in _DEFAULT_ZERO_COLUMNS:
        output[column] = output[column].fillna(0)

    # Cast integer fields only after filling optional count columns.
    for column in _INT_COLUMNS:
        output[column] = pd.to_numeric(output[column], errors="coerce").astype("Int64")

    output["gameweek"] = output["gameweek"].astype("Int64")
    output["player_id"] = output["player_id"].astype("Int64")
    output["team_id"] = output["team_id"].astype("Int64")
    output["fixture_id"] = output["fixture_id"].astype("Int64")
    output["opponent_team_id"] = output["opponent_team_id"].astype("Int64")

    for column in _FLOAT_COLUMNS:
        output[column] = pd.to_numeric(output[column], errors="coerce").astype("Float64")

    output = output.loc[:, PLAYER_GW_COLUMNS]
    output = output.sort_values(["gameweek", "player_id"], kind="stable").reset_index(drop=True)
    validate_player_gw(output)
    return output


def load_historical_player_gw(path: str | Path, season: str) -> pd.DataFrame:
    """Load and normalize a historical ``gws/merged_gw.csv`` file."""
    frame = pd.read_csv(path)
    return normalize_player_gw(frame, season)


def write_player_gw(frame: pd.DataFrame, destination: str | Path) -> Path:
    """Validate and write a canonical player_gw CSV."""
    validate_player_gw(frame)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False)
    return destination
