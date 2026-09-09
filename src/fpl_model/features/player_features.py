from __future__ import annotations

import pandas as pd


def rolling_mean(
    frame: pd.DataFrame, column: str, window: int
) -> pd.Series:
    """Calculate a per-player rolling mean using only prior gameweeks."""
    return frame.groupby("player_id")[column].transform(
        lambda values: values.shift(1).rolling(window, min_periods=1).mean()
    )
