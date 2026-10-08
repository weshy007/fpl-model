from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from .points import PointsPredictor

BASELINES = {
    "base_last_gw": "pts_last",
    "base_roll3": "pts_roll3",
    "base_roll5": "pts_roll5",
}


def walk_forward_predictions(
    table: pd.DataFrame,
    features: list[str],
    test_season: str,
    estimator_factory: Callable,
    retrain_every: int = 4,
    target: str = "next_gw_points",
) -> pd.DataFrame:
    """Chronological validation: fit only on Gameweeks before each test block.

    Training rows always have ``time_idx`` strictly below the first Gameweek
    being predicted, so no future outcome is ever seen. Returns the test rows
    with the model prediction and baseline predictions attached.
    """
    test_times = sorted(table.loc[table["season"] == test_season, "time_idx"].unique())
    if not test_times:
        raise ValueError(f"No rows for test season {test_season!r}")

    blocks = []
    for start in range(0, len(test_times), retrain_every):
        block = test_times[start : start + retrain_every]
        train = table[table["time_idx"] < block[0]].dropna(subset=[target])
        if train.empty:
            raise ValueError(
                f"No training rows before time_idx {block[0]}; "
                "include earlier seasons or choose a later test season."
            )
        test = table[table["time_idx"].isin(block)].copy()

        estimator = estimator_factory()
        estimator.fit(train[features], train[target])
        test["pred_model"] = PointsPredictor(estimator).predict(test[features])

        fallback = train[target].mean()  # cold start: players with no history
        position_mean = train.groupby("position")[target].mean()
        test["base_position_mean"] = test["position"].map(position_mean).fillna(fallback)
        for name, column in BASELINES.items():
            test[name] = test[column].fillna(fallback)
        blocks.append(test)

    return pd.concat(blocks, ignore_index=True)
