from __future__ import annotations


def transfer_gain(expected_in: float, expected_out: float) -> float:
    """Calculate raw expected-point difference for a transfer."""
    return expected_in - expected_out
