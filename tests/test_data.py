import pandas as pd
import pytest

from src.data.validation import require_columns


def test_require_columns_accepts_complete_frame():
    frame = pd.DataFrame({"player_id": [1], "gameweek": [1]})
    require_columns(frame, ["player_id", "gameweek"])


def test_require_columns_rejects_missing_columns():
    frame = pd.DataFrame({"player_id": [1]})
    with pytest.raises(ValueError, match="gameweek"):
        require_columns(frame, ["player_id", "gameweek"])
