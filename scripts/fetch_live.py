"""Download the current season from the official FPL API (run from a machine with access)."""

from __future__ import annotations

import argparse
from pathlib import Path

from fpl_model.data.fpl_api import fetch_season_files
from fpl_model.utils.config import load_config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season", help="Season label, default: last one in the config")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    season = args.season or config["data"]["seasons"][-1]
    target = Path(config["data"]["raw_path"]) / season
    print(f"Fetching {season} from the official FPL API into {target} ...")
    fetch_season_files(target)
    print("Done. Next: python scripts/predict_upcoming.py")
