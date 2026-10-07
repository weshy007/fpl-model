from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


REQUIRED_PLAYER_GW_COLUMNS = {
    "name",
    "team",
    "position",
    "total_points",
    "minutes",
}


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
    if (values < 0).any():
        raise ValueError(f"Column {column!r} contains negative values")
