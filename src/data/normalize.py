from __future__ import annotations

from pathlib import Path

import pandas as pd

from .validation import require_columns, validate_points


POSITION_MAP = {
    1: "GK",
    2: "DEF",
    3: "MID",
    4: "FWD",
}


def load_historical_player_gw(path: str | Path, season: str) -> pd.DataFrame:
    """Load and normalize a historical merged GW file.

    The returned table is deliberately close to the source schema. Feature
    engineering happens later so we can audit the raw-to-feature transformation.
    """
    frame = pd.read_csv(path)
    require_columns(frame, ["name", "team", "element", "event", "total_points", "minutes"])
    validate_points(frame)

    frame = frame.copy()
    frame["season"] = season
    frame["player_id"] = frame["element"].astype("int64")
    frame["gameweek"] = frame["event"].astype("int64")
    frame["position"] = frame.get("element_type", pd.Series(index=frame.index)).map(POSITION_MAP)

    return frame
