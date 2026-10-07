from __future__ import annotations


def validate_squad_size(player_ids: list[int], expected_size: int = 15) -> None:
    """Validate the number of players in a squad."""
    if len(player_ids) != expected_size:
        raise ValueError(f"Expected {expected_size} players, got {len(player_ids)}")
