from __future__ import annotations

import pandas as pd


def sort_player_gameweeks(frame: pd.DataFrame) -> pd.DataFrame:
    """Return player gameweeks ordered chronologically."""
    return frame.sort_values(["player_id", "gameweek"]).reset_index(drop=True)
