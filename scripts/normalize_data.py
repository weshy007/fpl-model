from __future__ import annotations

import argparse
import sys


from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.normalize import load_historical_player_gw, write_player_gw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize raw FPL player/Gameweek data.")
    parser.add_argument(
        "--season",
        action="append",
        dest="seasons",
        required=True,
        help="Season to normalize, e.g. 2025-26. May be supplied multiple times.",
    )
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    for season in args.seasons:
        source = args.raw_root / season / "merged_gw.csv"
        destination = args.processed_root / season / "player_gw.csv"

        if not source.exists():
            raise SystemExit(f"Missing raw file: {source}")

        frame = load_historical_player_gw(source, season)
        write_player_gw(frame, destination)
        print(f"{season}: {len(frame):,} rows -> {destination}")


if __name__ == "__main__":
    main()
