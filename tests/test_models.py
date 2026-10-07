import numpy as np
from sklearn.dummy import DummyRegressor

from fpl_model.models.evaluation import regression_metrics
from fpl_model.models.points import PointsPredictor


def test_points_predictions_are_non_negative():
    model = DummyRegressor(strategy="constant", constant=-10)
    model.fit(np.array([[1], [2]]), np.array([1, 2]))
    predictor = PointsPredictor(model)
    predictions = predictor.predict(np.array([[3], [4]]))
    assert np.all(predictions >= 0)


def test_regression_metrics():
    metrics = regression_metrics([1, 2, 3], [1, 3, 2])
    assert set(metrics) == {"mae", "rmse"}
    assert metrics["mae"] > 0
