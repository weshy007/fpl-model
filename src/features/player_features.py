from __future__ import annotations

import pandas as pd


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
