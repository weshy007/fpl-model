from __future__ import annotations

from collections.abc import Sized


def validate_squad_size(squad: Sized) -> None:
    """Validate the standard Fantasy Premier League squad size."""
    if len(squad) != 15:
        raise ValueError("Squad must contain 15 players")
