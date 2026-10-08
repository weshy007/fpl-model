from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import pandas as pd

from ..features.player_features import TARGET, build_model_table, feature_columns
from ..models.evaluation import paired_gap, per_gameweek_metrics, summarize
from ..models.points import make_estimator
from ..models.validation import walk_forward_predictions
from ..optimization.simulate import backtest_decisions
from ..utils.config import load_config
from .ingestion import load_player_gw

log = logging.getLogger(__name__)
PRED_COLS = ["pred_model", "base_last_gw", "base_roll3", "base_roll5", "base_position_mean"]


def table_path(config: dict) -> Path:
    return Path(config["data"]["interim_path"]) / "model_table.csv"


def build_features(config: dict) -> Path:
    """Build and save the leakage-free player-Gameweek modelling table."""
    frame = load_player_gw(config["data"]["seasons"], config["data"]["processed_path"])
    table = build_model_table(
        frame,
        tuple(config["features"]["rolling_windows"]),
        config["features"]["form_window"],
    )
    path = table_path(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, index=False)
    log.info("Wrote %s rows to %s", f"{len(table):,}", path)
    return path


def load_table(config: dict) -> pd.DataFrame:
    path = table_path(config)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run scripts/build_features.py first.")
    return pd.read_csv(path)


def _feature_list(config: dict) -> list[str]:
    return feature_columns(
        tuple(config["features"]["rolling_windows"]), config["features"]["form_window"]
    )


def run(config_path: str = "configs/config.yaml") -> dict:
    """Walk-forward backtest, then fit and save the final model."""
    config = load_config(config_path)
    ev, seed = config["evaluation"], config["model"]["random_seed"]
    features = _feature_list(config)
    table = load_table(config)
    params = config["model"].get("lightgbm")

    def factory():
        return make_estimator(params, seed)

    log.info("Walk-forward validation on %s", ev["test_season"])
    predictions = walk_forward_predictions(
        table, features, ev["test_season"], factory, ev["retrain_every"]
    )
    scored = predictions[predictions["prior_gws"] >= ev["min_history"]]

    per_gw = per_gameweek_metrics(scored, PRED_COLS, TARGET, ev["top_k"])
    summary = summarize(per_gw)
    decisions = backtest_decisions(scored, PRED_COLS)
    xi_summary = decisions.groupby("predictor")["xi_points"].mean()

    gaps = {
        f"{metric}_vs_{base}": paired_gap(per_gw, metric, "pred_model", base)
        for base in ("base_roll5", "base_roll3")
        for metric in ("mae", "spearman", "captain_points")
    }
    for base in ("base_roll5", "base_roll3"):
        gaps[f"xi_points_vs_{base}"] = paired_gap(decisions, "xi_points", "pred_model", base)

    out = Path(ev["results_path"])
    out.mkdir(parents=True, exist_ok=True)
    per_gw.to_csv(out / "per_gameweek.csv", index=False)
    decisions.to_csv(out / "decisions.csv", index=False)
    summary.assign(xi_points=xi_summary).to_csv(out / "summary.csv")
    (out / "paired_gaps.json").write_text(json.dumps(gaps, indent=2), encoding="utf-8")

    # Final model: all data available, for predicting upcoming Gameweeks.
    final = factory()
    labelled = table.dropna(subset=[TARGET])
    final.fit(labelled[features], labelled[TARGET])
    model_path = Path(config["model"]["path"])
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"estimator": final, "features": features}, model_path)

    log.info("\n%s", summary.assign(xi_points=xi_summary).round(3).to_string())
    return {"summary": summary.assign(xi_points=xi_summary), "gaps": gaps}
