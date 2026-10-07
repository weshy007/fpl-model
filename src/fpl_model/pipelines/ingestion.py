from __future__ import annotations

from pathlib import Path

import pandas as pd

_FLOAT_COLUMNS = ["xg", "xa", "xgi", "xgc", "influence", "creativity", "threat", "ict_index"]


def load_player_gw(seasons: list[str], processed_root: str | Path) -> pd.DataFrame:
    """Read normalized ``player_gw.csv`` files and restore the canonical dtypes."""
    frames = []
    for season in seasons:
        path = Path(processed_root) / season / "player_gw.csv"
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found. Run scripts/ingest_data.py and scripts/normalize_data.py first."
            )
        frames.append(pd.read_csv(path, parse_dates=["kickoff_time"]))
    frame = pd.concat(frames, ignore_index=True)
    frame[_FLOAT_COLUMNS] = frame[_FLOAT_COLUMNS].astype("float64")
    return frame
