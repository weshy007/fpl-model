from __future__ import annotations

import argparse

from src.pipelines.upcoming import run
from src.utils.logging import configure_logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict points for the upcoming Gameweek.")
    parser.add_argument("--season", help="default: last season in the config")
    parser.add_argument("--gameweek", type=int, help="default: next unfinished Gameweek")
    parser.add_argument("--note", help="optional banner text shown on the dashboard")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()
    configure_logging()

    result = run(args.season, args.gameweek, args.config, args.note)
    meta = result["meta"]
    print(f"\nGW{meta['gameweek']} top 10 expected points:")
    cols = ["web_name", "team", "position", "opponent", "price", "expected_points", "availability"]
    print(result["predictions"][cols].head(10).round(2).to_string(index=False))
    print(f"\nDashboard: {result['path']}")
