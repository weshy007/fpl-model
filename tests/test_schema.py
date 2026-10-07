import pandas as pd
import pytest

from fpl_model.data.normalize import normalize_player_gw
from fpl_model.data.schema import PLAYER_GW_COLUMNS
from fpl_model.data.validation import validate_player_gw
from tests.test_normalize import raw_row


def test_player_gw_column_order_is_canonical():
    frame = normalize_player_gw(pd.DataFrame([raw_row()]), "2025-26")
    assert tuple(frame.columns) == PLAYER_GW_COLUMNS


def test_player_gw_requires_positive_identifiers():
    frame = normalize_player_gw(pd.DataFrame([raw_row()]), "2025-26")
    frame.loc[0, "player_id"] = 0

    with pytest.raises(ValueError, match="player_id.*positive"):
        validate_player_gw(frame)


def test_player_gw_rejects_missing_name():
    frame = normalize_player_gw(pd.DataFrame([raw_row()]), "2025-26")
    frame.loc[0, "name"] = ""

    with pytest.raises(ValueError, match="name"):
        validate_player_gw(frame)


def test_player_gw_rejects_invalid_position():
    frame = normalize_player_gw(pd.DataFrame([raw_row()]), "2025-26")
    frame.loc[0, "position"] = "ST"

    with pytest.raises(ValueError, match="Invalid position"):
        validate_player_gw(frame)
