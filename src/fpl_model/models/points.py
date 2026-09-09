from __future__ import annotations

from typing import Any

import numpy as np


class PointsPredictor:
    def __init__(self, model: Any) -> None:
        self.model = model

    def predict(self, features: Any) -> np.ndarray:
        """Predict points and prevent impossible negative values."""
        return np.maximum(np.asarray(self.model.predict(features)), 0)
