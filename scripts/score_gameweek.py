from __future__ import annotations

import argparse
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from src.pipelines.track import score_gameweek

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score a finished Gameweek's saved predictions.")
    parser.add_argument("--season", help="default: last season in the config")
    parser.add_argument("--gameweek", type=int, help="default: latest Gameweek with results")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    result = score_gameweek(args.season, args.gameweek, args.config)
    gw = int(result["gameweek"].iloc[0])
    print(f"\nGW{gw} - how each predictor did (lower MAE / higher everything else is better):")
    print(result.drop(columns=["season", "gameweek"]).round(2).to_string(index=False))
