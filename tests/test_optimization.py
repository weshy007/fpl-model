import pytest

from fpl_model.optimization.lineup import validate_formation
from fpl_model.optimization.squad import validate_squad_size
from fpl_model.optimization.transfers import transfer_gain


def test_valid_formation():
    validate_formation(defenders=4, midfielders=4, forwards=2)


def test_invalid_formation():
    with pytest.raises(ValueError):
        validate_formation(defenders=2, midfielders=5, forwards=3)


def test_squad_size():
    validate_squad_size(list(range(15)))


def test_transfer_gain():
    assert transfer_gain(7.5, 5.0) == 2.5
