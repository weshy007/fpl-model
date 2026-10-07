from __future__ import annotations

import argparse
import logging

from fpl_model.pipelines.training import build_features
from fpl_model.utils.config import load_config
from fpl_model.utils.logging import configure_logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the player-Gameweek feature table.")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()
    configure_logging()
    build_features(load_config(args.config))
    logging.getLogger(__name__).info("done")
