from __future__ import annotations

import argparse
from pathlib import Path

from src.data.download import (
    download_current_season,
    download_historical_season,
    write_manifest,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download FPL source data.")
    parser.add_argument(
        "--season",
        action="append",
        dest="seasons",
        help="Season to download, e.g. 2025-26. May be supplied multiple times.",
    )
    parser.add_argument(
        "--current-season",
        metavar="SEASON",
        help="Download official API snapshots into the given season folder, e.g. 2026-27.",
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=Path("data/raw"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = []

    for season in args.seasons or []:
        records.extend(download_historical_season(season, args.raw_root))

    if args.current_season:
        records.extend(download_current_season(args.current_season, args.raw_root))

    if not records:
        raise SystemExit("Provide --season YYYY-YY and/or --current-season YYYY-YY")

    write_manifest(records, args.raw_root / "manifest.json")
    print(f"Downloaded {len(records)} files.")


if __name__ == "__main__":
    main()
