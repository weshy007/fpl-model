from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    """Return basic regression metrics."""
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
    }


def per_gameweek_metrics(
    predictions: pd.DataFrame,
    pred_cols: list[str],
    target: str = "next_gw_points",
    top_k: int = 10,
) -> pd.DataFrame:
    """MAE, rank correlation, top-K points and captain points per Gameweek."""
    rows = []
    for time_idx, gw in predictions.groupby("time_idx"):
        for col in pred_cols:
            actual, pred = gw[target], gw[col]
            ranked = gw.assign(_p=pred).sort_values("_p", ascending=False, kind="stable")
            rows.append(
                {
                    "time_idx": time_idx,
                    "gameweek": int(gw["gameweek"].iloc[0]),
                    "predictor": col,
                    "mae": float((actual - pred).abs().mean()),
                    "spearman": float(stats.spearmanr(pred, actual)[0]),
                    "top_k_points": float(ranked[target].head(top_k).mean()),
                    "captain_points": float(ranked[target].iloc[0]),
                }
            )
    return pd.DataFrame(rows)


def summarize(per_gw: pd.DataFrame) -> pd.DataFrame:
    """Average the per-Gameweek metrics for each predictor."""
    cols = ["mae", "spearman", "top_k_points", "captain_points"]
    return per_gw.groupby("predictor")[cols].mean().sort_values("spearman", ascending=False)


def paired_gap(per_gw: pd.DataFrame, metric: str, a: str, b: str) -> dict[str, float]:
    """Mean per-Gameweek difference ``a - b`` with a t-based 95% interval."""
    wide = per_gw.pivot(index="time_idx", columns="predictor", values=metric)
    diff = (wide[a] - wide[b]).dropna()
    mean, sem = float(diff.mean()), float(stats.sem(diff))
    half = float(stats.t.ppf(0.975, len(diff) - 1) * sem)
    return {"mean_diff": mean, "ci_low": mean - half, "ci_high": mean + half, "n_gws": len(diff)}
