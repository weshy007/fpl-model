from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.base import RegressorMixin


@dataclass
class PointsPredictor:
    """Interface for an expected-points model."""
    estimator: RegressorMixin

    def predict(self, features: np.ndarray) -> np.ndarray:
        predictions = self.estimator.predict(features)
        return np.maximum(predictions, 0)
