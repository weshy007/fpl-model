from __future__ import annotations

import argparse

from src.pipelines.training import run
from src.utils.logging import configure_logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtest and train the points model.")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()
    configure_logging()
    run(args.config)
