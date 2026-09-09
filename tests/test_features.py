import pandas as pd

from fpl_model.features.player_features import rolling_mean


def test_rolling_mean_does_not_use_current_gameweek():
    frame = pd.DataFrame(
        {"player_id": [1, 1, 1], "gameweek": [1, 2, 3], "points": [10, 20, 30]}
    )
    result = rolling_mean(frame, "points", window=2)
    assert pd.isna(result.iloc[0])
    assert result.iloc[1] == 10
    assert result.iloc[2] == 15
