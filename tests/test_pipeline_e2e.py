import pandas as pd
import yaml

from fpl_model.pipelines import prediction, training
from tests.test_pipeline import synthetic_player_gw


def write_season(root, season, seed):
    frame = synthetic_player_gw(seed=seed).assign(season=season)
    for column in ("xg", "xa", "xgc"):
        frame[column] = float("nan")
    frame["influence"] = frame["creativity"] = frame["threat"] = 1.0
    frame["kickoff_time"] = pd.Timestamp("2025-08-01")
    path = root / "processed" / season
    path.mkdir(parents=True)
    frame.to_csv(path / "player_gw.csv", index=False)


def test_build_train_predict_roundtrip(tmp_path):
    write_season(tmp_path, "2024-25", 0)
    write_season(tmp_path, "2025-26", 1)
    config = {
        "data": {
            "processed_path": str(tmp_path / "processed"),
            "interim_path": str(tmp_path / "interim"),
            "seasons": ["2024-25", "2025-26"],
        },
        "model": {
            "random_seed": 0,
            "path": str(tmp_path / "model.joblib"),
            "lightgbm": {"n_estimators": 5, "min_child_samples": 2},
        },
        "features": {"rolling_windows": [3, 5], "form_window": 5},
        "evaluation": {
            "test_season": "2025-26",
            "retrain_every": 6,
            "min_history": 1,
            "top_k": 5,
            "results_path": str(tmp_path / "results"),
        },
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))

    training.build_features(config)
    result = training.run(str(config_path))

    assert {"pred_model", "base_roll5"} <= set(result["summary"].index)
    assert (tmp_path / "results" / "summary.csv").exists()
    assert (tmp_path / "model.joblib").exists()

    squad = prediction.run("2025-26", 12, str(config_path))
    assert len(squad) == 15 and squad["in_xi"].sum() == 11
