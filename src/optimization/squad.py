from __future__ import annotations

SQUAD_SIZE = 15
SQUAD_POSITIONS = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}
BUDGET = 1000  # £100.0m in FPL price units (tenths of a million)
MAX_PER_CLUB = 3


def validate_squad_size(player_ids: list[int], expected_size: int = SQUAD_SIZE) -> None:
    """Validate the number of players in a squad."""
    if len(player_ids) != expected_size:
        raise ValueError(f"Expected {expected_size} players, got {len(player_ids)}")
