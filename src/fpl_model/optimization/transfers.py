from __future__ import annotations


def transfer_gain(incoming_value: float, outgoing_value: float) -> float:
    """Return the value gained by replacing one player with another."""
    return incoming_value - outgoing_value
