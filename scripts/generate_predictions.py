from __future__ import annotations

import argparse

from src.pipelines.prediction import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recommend a squad for one Gameweek.")
    parser.add_argument("--season")
    parser.add_argument("--gameweek", type=int)
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    squad = run(args.season, args.gameweek, args.config)
    cols = [
        "name",
        "position",
        "value",
        "pred_points",
        "in_xi",
        "captain",
        "vice_captain",
        "bench_order",
    ]
    print(squad[cols].to_string(index=False))
    print(
        "\nNote: the saved model is trained on all processed seasons, so replaying a "
        "historical Gameweek is in-sample. Use the backtest for honest evaluation."
    )
