from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import LinearConstraint, milp

from .squad import BUDGET, MAX_PER_CLUB, SQUAD_POSITIONS, SQUAD_SIZE

# (min, max) outfield players in the starting XI per position
XI_LIMITS = {"GK": (1, 1), "DEF": (3, 5), "MID": (2, 5), "FWD": (1, 3)}
BENCH_WEIGHT = 0.1  # value of bench points relative to starters


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


def pick_squad(
    players: pd.DataFrame,
    pred_col: str,
    budget: int = BUDGET,
) -> pd.DataFrame:
    """Choose the best 15-man squad, XI, captain and vice-captain.

    Solves ``maximize sum(pred * (xi + BENCH_WEIGHT * squad))`` subject to the
    budget, position, club and formation rules. ``players`` needs the columns
    ``position``, ``team_id``, ``value`` and ``pred_col``.

    Returns the 15 selected rows with boolean ``in_xi``, ``captain``,
    ``vice_captain`` and a ``bench_order`` (0 = not on bench).
    """
    p = players.reset_index(drop=True)
    n = len(p)
    pred = p[pred_col].to_numpy(dtype=float)

    # variable layout: [squad_0..squad_n-1, xi_0..xi_n-1]
    cost = -np.concatenate([BENCH_WEIGHT * pred, pred])
    rows, lows, highs = [], [], []

    def add(squad_coef, xi_coef, low, high):
        rows.append(np.concatenate([squad_coef, xi_coef]))
        lows.append(low)
        highs.append(high)

    zeros, ones = np.zeros(n), np.ones(n)
    add(ones, zeros, SQUAD_SIZE, SQUAD_SIZE)
    add(zeros, ones, 11, 11)
    add(p["value"].to_numpy(dtype=float), zeros, 0, budget)
    for position, count in SQUAD_POSITIONS.items():
        mask = (p["position"] == position).to_numpy(dtype=float)
        add(mask, zeros, count, count)
        low, high = XI_LIMITS[position]
        add(zeros, mask, low, high)
    for team in p["team_id"].unique():
        add((p["team_id"] == team).to_numpy(dtype=float), zeros, 0, MAX_PER_CLUB)
    for i in range(n):  # xi_i <= squad_i
        coef_s, coef_x = np.zeros(n), np.zeros(n)
        coef_s[i], coef_x[i] = -1, 1
        add(coef_s, coef_x, -np.inf, 0)

    result = milp(
        c=cost,
        constraints=LinearConstraint(np.array(rows), lows, highs),
        integrality=np.ones(2 * n),
        bounds=(0, 1),
    )
    if not result.success:
        raise RuntimeError(f"Squad optimisation failed: {result.message}")

    chosen = np.round(result.x).astype(bool)
    squad = p.loc[chosen[:n]].copy()
    squad["in_xi"] = chosen[n:][chosen[:n]]

    xi = squad[squad["in_xi"]].sort_values(pred_col, ascending=False, kind="stable")
    squad["captain"] = squad.index == xi.index[0]
    squad["vice_captain"] = squad.index == xi.index[1]

    bench = squad[~squad["in_xi"]]
    bench_gk = bench[bench["position"] == "GK"]
    bench_out = bench[bench["position"] != "GK"].sort_values(
        pred_col, ascending=False, kind="stable"
    )
    squad["bench_order"] = 0
    for order, idx in enumerate([*bench_gk.index, *bench_out.index], start=1):
        squad.loc[idx, "bench_order"] = order
    return squad.sort_values(["in_xi", pred_col], ascending=False, kind="stable")
