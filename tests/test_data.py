import pandas as pd
import pytest

from fpl_model.data.preprocessing import sort_player_gameweeks
from fpl_model.data.validation import require_columns


def test_require_columns_accepts_complete_frame():
    frame = pd.DataFrame({"player_id": [1], "gameweek": [1]})
    require_columns(frame, ["player_id", "gameweek"])


def test_require_columns_rejects_missing_columns():
    frame = pd.DataFrame({"player_id": [1]})
    with pytest.raises(ValueError, match="gameweek"):
        require_columns(frame, ["player_id", "gameweek"])


def test_sort_player_gameweeks_is_chronological():
    frame = pd.DataFrame({"player_id": [1, 1, 2], "gameweek": [2, 1, 1]})
    result = sort_player_gameweeks(frame)
    assert result[["player_id", "gameweek"]].values.tolist() == [[1, 1], [1, 2], [2, 1]]
