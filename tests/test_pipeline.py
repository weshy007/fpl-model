import numpy as np
import pandas as pd
import pytest

from src.features.player_features import (
    TARGET,
    build_model_table,
    feature_columns,
)
from src.models.evaluation import paired_gap, per_gameweek_metrics
from src.models.points import make_estimator
from src.models.validation import walk_forward_predictions
from src.optimization.lineup import pick_squad
from src.optimization.simulate import score_squad

POSITIONS = ["GK"] * 4 + ["DEF"] * 10 + ["MID"] * 10 + ["FWD"] * 6


def synthetic_player_gw(n_gws=12, seed=0) -> pd.DataFrame:
    """30 players across 10 teams, one fixture each per Gameweek."""
    rng = np.random.default_rng(seed)
    rows = []
    for gw in range(1, n_gws + 1):
        for pid, position in enumerate(POSITIONS, start=1):
            team = (pid - 1) % 10 + 1
            rows.append(
                {
                    "season": "2025-26",
                    "gameweek": gw,
                    "player_id": pid,
                    "name": f"Player {pid}",
                    "team_id": team,
                    "position": position,
                    "fixture_id": gw * 100 + (team + 1) // 2,
                    "opponent_team_id": team % 10 + 1,
                    "was_home": team % 2 == 0,
                    "minutes": 90,
                    "total_points": int(rng.integers(0, 10)),
                    "goals_conceded": int(rng.integers(0, 3)),
                    "bps": 20,
                    "ict_index": 5.0,
                    "xgi": np.nan,
                    "selected": 1000,
                    "value": 50,
                }
            )
    return pd.DataFrame(rows)


def test_features_do_not_use_current_or_future_gameweeks():
    frame = synthetic_player_gw()
    base = build_model_table(frame)

    changed = frame.copy()
    late = changed["gameweek"] >= 8
    changed.loc[late, ["total_points", "minutes", "bps", "goals_conceded"]] = 99
    altered = build_model_table(changed)

    features = feature_columns()
    early = base["gameweek"] <= 8  # GW8 features may only depend on GW1-7
    pd.testing.assert_frame_equal(
        base.loc[early, features].reset_index(drop=True),
        altered.loc[early, features].reset_index(drop=True),
    )
    assert base[TARGET].tolist() != altered[TARGET].tolist()


def test_double_gameweek_collapses_to_one_row():
    frame = synthetic_player_gw(n_gws=4)
    extra = frame[(frame["gameweek"] == 3) & (frame["player_id"] == 1)].copy()
    extra["fixture_id"] += 1000
    extra["total_points"] = 5
    table = build_model_table(pd.concat([frame, extra], ignore_index=True))
    row = table[(table["gameweek"] == 3) & (table["name"] == "Player 1")]
    assert len(row) == 1
    assert row["n_fixtures"].iloc[0] == 2


def two_season_table() -> pd.DataFrame:
    old = synthetic_player_gw(seed=0).assign(season="2024-25")
    new = synthetic_player_gw(seed=1)
    return build_model_table(pd.concat([old, new], ignore_index=True))


def test_walk_forward_never_trains_on_test_block():
    table = two_season_table()
    first_test = int(table.loc[table["season"] == "2025-26", "time_idx"].min())
    max_train_times = []

    class Spy:
        def __init__(self):
            self.inner = make_estimator({"n_estimators": 5, "min_child_samples": 2})

        def fit(self, x, y):
            max_train_times.append(int(table.loc[x.index, "time_idx"].max()))
            return self.inner.fit(x, y)

        def predict(self, x):
            return self.inner.predict(x)

    preds = walk_forward_predictions(table, feature_columns(), "2025-26", Spy, retrain_every=3)
    # Each refit sees everything up to, and nothing from, its test block.
    assert max_train_times == [first_test - 1 + 3 * k for k in range(4)]
    assert set(preds["season"]) == {"2025-26"}
    assert len(preds) == (table["season"] == "2025-26").sum()
    assert preds["pred_model"].notna().all()


def test_walk_forward_needs_earlier_training_data():
    table = build_model_table(synthetic_player_gw())
    with pytest.raises(ValueError, match="No training rows"):
        walk_forward_predictions(table, feature_columns(), "2025-26", make_estimator)


def test_walk_forward_rejects_unknown_season():
    table = build_model_table(synthetic_player_gw())
    with pytest.raises(ValueError):
        walk_forward_predictions(table, feature_columns(), "1999-00", make_estimator)


def test_pick_squad_respects_fpl_rules():
    pool = synthetic_player_gw(n_gws=1)
    pool["pred"] = np.random.default_rng(1).random(len(pool)) * 8
    pool["next_gw_points"] = pool["total_points"]
    squad = pick_squad(pool, "pred")

    assert len(squad) == 15
    assert squad["value"].sum() <= 1000
    assert squad["team_id"].value_counts().max() <= 3
    assert squad["position"].value_counts().to_dict() == {"DEF": 5, "MID": 5, "FWD": 3, "GK": 2}
    xi = squad[squad["in_xi"]]
    assert len(xi) == 11
    counts = xi["position"].value_counts()
    assert counts["GK"] == 1 and 3 <= counts["DEF"] <= 5
    assert 2 <= counts["MID"] <= 5 and 1 <= counts["FWD"] <= 3
    assert squad["captain"].sum() == 1 and squad["vice_captain"].sum() == 1
    assert xi.loc[xi["captain"], "pred"].iloc[0] == xi["pred"].max()
    assert sorted(squad.loc[~squad["in_xi"], "bench_order"]) == [1, 2, 3, 4]
    assert score_squad(squad) >= xi["next_gw_points"].sum()


def test_per_gameweek_metrics_and_paired_gap():
    rng = np.random.default_rng(2)
    rows = []
    for t in range(10):
        actual = rng.integers(0, 10, 30)
        rows.append(
            pd.DataFrame(
                {
                    "time_idx": t,
                    "gameweek": t + 1,
                    "next_gw_points": actual,
                    "good": actual + rng.normal(0, 1, 30),
                    "bad": rng.random(30) * 10,
                }
            )
        )
    per_gw = per_gameweek_metrics(pd.concat(rows), ["good", "bad"])
    gap = paired_gap(per_gw, "mae", "good", "bad")
    assert gap["mean_diff"] < 0 and gap["ci_high"] < 0
    assert gap["n_gws"] == 10
