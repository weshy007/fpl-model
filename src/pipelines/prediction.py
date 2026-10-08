from __future__ import annotations

import joblib
import pandas as pd

from ..models.points import PointsPredictor
from ..optimization.lineup import pick_squad
from ..utils.config import load_config
from .training import load_table


def run(
    season: str | None = None,
    gameweek: int | None = None,
    config_path: str = "configs/config.yaml",
) -> pd.DataFrame:
    """Predict a Gameweek from the table and recommend squad, XI and captain.

    Works on Gameweeks present in the processed data (historical replay). The
    features for that Gameweek only use earlier results. Live ingestion of an
    upcoming, not-yet-played Gameweek is not implemented yet.
    """
    config = load_config(config_path)
    bundle = joblib.load(config["model"]["path"])
    table = load_table(config)

    season = season or table["season"].iloc[-1]
    in_season = table[table["season"] == season]
    gameweek = gameweek or int(in_season["gameweek"].max())
    pool = in_season[in_season["gameweek"] == gameweek].copy()
    if pool.empty:
        raise ValueError(f"No rows for {season} GW{gameweek}")

    pool["pred_points"] = PointsPredictor(bundle["estimator"]).predict(pool[bundle["features"]])
    return pick_squad(pool, "pred_points")
