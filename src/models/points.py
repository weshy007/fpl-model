from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from lightgbm import LGBMRegressor
from sklearn.base import RegressorMixin

DEFAULT_PARAMS = {
    "n_estimators": 300,
    "learning_rate": 0.03,
    "num_leaves": 31,
    "min_child_samples": 50,
    "subsample": 0.8,
    "subsample_freq": 1,
    "colsample_bytree": 0.8,
}


@dataclass
class PointsPredictor:
    """Expected-points model wrapper (predictions are floored at zero)."""

    estimator: RegressorMixin

    def predict(self, features: np.ndarray) -> np.ndarray:
        predictions = self.estimator.predict(features)
        return np.maximum(predictions, 0)


def make_estimator(params: dict | None = None, seed: int = 42) -> LGBMRegressor:
    """LightGBM regressor with L2 loss, i.e. it estimates expected points."""
    merged = {**DEFAULT_PARAMS, **(params or {})}
    return LGBMRegressor(random_state=seed, verbosity=-1, **merged)
