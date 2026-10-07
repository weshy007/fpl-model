from __future__ import annotations


def validate_formation(
    defenders: int,
    midfielders: int,
    forwards: int,
) -> None:
    """Validate a basic FPL-style outfield formation."""
    total = defenders + midfielders + forwards

    if total != 10:
        raise ValueError("A starting XI must contain 10 outfield players.")
    if not 3 <= defenders <= 5:
        raise ValueError("Defenders must be between 3 and 5.")
    if not 2 <= midfielders <= 5:
        raise ValueError("Midfielders must be between 2 and 5.")
    if not 1 <= forwards <= 3:
        raise ValueError("Forwards must be between 1 and 3.")
