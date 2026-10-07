from __future__ import annotations

import numpy as np
import pandas as pd

from .schema import (
    PLAYER_GW_REQUIRED_COLUMNS,
    PLAYER_GW_SCHEMA,
    VALID_POSITIONS,
)


def require_columns(frame: pd.DataFrame, columns: list[str] | set[str]) -> None:
    """Raise a useful error if required columns are missing."""
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def require_unique_key(frame: pd.DataFrame, columns: list[str]) -> None:
    """Validate that a set of columns forms a unique key."""
    duplicates = frame.duplicated(columns, keep=False)
    if duplicates.any():
        sample = frame.loc[duplicates, columns].head(10).to_dict("records")
        raise ValueError(f"Duplicate key rows found for {columns}: {sample}")


def validate_points(frame: pd.DataFrame, column: str = "total_points") -> None:
    """Validate that an FPL points column contains finite non-negative values."""
    values = pd.to_numeric(frame[column], errors="coerce")
    if values.isna().any():
        raise ValueError(f"Column {column!r} contains non-numeric values")
    if not np.isfinite(values).all():
        raise ValueError(f"Column {column!r} contains non-finite values")
    if (values < 0).any():
        raise ValueError(f"Column {column!r} contains negative values")


def validate_player_gw(frame: pd.DataFrame) -> None:
    """Validate the canonical player/Gameweek table.

    This is intentionally strict: downstream feature engineering assumes one
    row per player per Gameweek and a stable set of identifiers/types.
    """
    require_columns(frame, set(PLAYER_GW_REQUIRED_COLUMNS))
    require_unique_key(frame, ["season", "gameweek", "player_id"])

    if frame.empty:
        raise ValueError("player_gw cannot be empty")

    if frame["season"].isna().any() or frame["season"].astype("string").str.len().eq(0).any():
        raise ValueError("Column 'season' contains missing or empty values")

    for column in ["gameweek", "player_id", "team_id", "fixture_id", "opponent_team_id"]:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any() or not np.isfinite(values).all():
            raise ValueError(f"Column {column!r} contains invalid numeric values")
        if (values <= 0).any():
            raise ValueError(f"Column {column!r} must contain positive values")

    if not frame["gameweek"].between(1, 38).all():
        raise ValueError("Column 'gameweek' must be between 1 and 38")

    if frame["name"].isna().any() or frame["name"].astype("string").str.strip().eq("").any():
        raise ValueError("Column 'name' contains missing or empty values")

    positions = set(frame["position"].dropna().astype(str))
    invalid_positions = sorted(positions - VALID_POSITIONS)
    if invalid_positions:
        raise ValueError(f"Invalid position values: {invalid_positions}")
    if frame["position"].isna().any():
        raise ValueError("Column 'position' contains missing values")

    for column in ["minutes", "starts", "goals_scored", "assists", "clean_sheets", "goals_conceded"]:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any() or not np.isfinite(values).all():
            raise ValueError(f"Column {column!r} contains invalid numeric values")
        if (values < 0).any():
            raise ValueError(f"Column {column!r} contains negative values")

    validate_points(frame)

    if not frame["was_home"].isin([True, False]).all():
        raise ValueError("Column 'was_home' must contain boolean values")

    expected_dtypes = {spec.name: spec.dtype for spec in PLAYER_GW_SCHEMA}
    for column, expected in expected_dtypes.items():
        if column not in frame.columns:
            continue
        actual = str(frame[column].dtype)
        if actual != expected:
            raise ValueError(
                f"Column {column!r} has dtype {actual!r}; expected {expected!r}"
            )
