from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def regression_metrics(
    actual: Sequence[float], predicted: Sequence[float]
) -> dict[str, float]:
    """Return standard regression error metrics."""
    errors = np.asarray(predicted, dtype=float) - np.asarray(actual, dtype=float)
    return {
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(errors**2))),
    }
