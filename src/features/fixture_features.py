from __future__ import annotations

import pandas as pd


def add_home_flag(
    frame: pd.DataFrame,
    home_team_column: str = "home_team_id",
    player_team_column: str = "team_id",
) -> pd.Series:
    """Return whether the player's team is the home team."""
    return frame[home_team_column].eq(frame[player_team_column]).astype("int8")
