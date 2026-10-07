from __future__ import annotations

import pandas as pd


def rolling_team_metric(
    frame: pd.DataFrame,
    value_column: str,
    window: int,
    team_column: str = "team_id",
) -> pd.Series:
    """Calculate a leakage-resistant rolling team metric."""
    return frame.groupby(team_column)[value_column].transform(
        lambda series: series.shift(1).rolling(window, min_periods=1).mean()
    )
