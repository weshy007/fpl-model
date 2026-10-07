from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.base import RegressorMixin


@dataclass
class MinutesPredictor:
    """Interface for an expected-minutes model."""
    estimator: RegressorMixin

    def predict(self, features: np.ndarray) -> np.ndarray:
        predictions = self.estimator.predict(features)
        return np.clip(predictions, 0, 90)
