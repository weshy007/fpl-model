from __future__ import annotations

import pandas as pd

from .lineup import pick_squad


def score_squad(squad: pd.DataFrame, actual_col: str = "next_gw_points") -> float:
    """Actual points of an XI plus the captain's doubled score.

    Simplified: no automatic substitutions, chips, transfers or hits.
    """
    starters = squad[squad["in_xi"]]
    return float(starters[actual_col].sum() + squad.loc[squad["captain"], actual_col].sum())


def backtest_decisions(
    predictions: pd.DataFrame,
    pred_cols: list[str],
    actual_col: str = "next_gw_points",
) -> pd.DataFrame:
    """Pick a fresh squad each Gameweek from each predictor and score it.

    This compares how useful each predictor is for lineup decisions on equal
    terms; it is not a full season simulation with a persistent squad.
    """
    rows = []
    for time_idx, gw in predictions.groupby("time_idx"):
        pool = gw.assign(oracle=gw[actual_col].astype(float))
        for col in [*pred_cols, "oracle"]:
            squad = pick_squad(pool, col)
            rows.append(
                {
                    "time_idx": time_idx,
                    "gameweek": int(gw["gameweek"].iloc[0]),
                    "predictor": col,
                    "xi_points": score_squad(squad, actual_col),
                }
            )
    return pd.DataFrame(rows)
