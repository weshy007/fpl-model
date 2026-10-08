import json
import re

import numpy as np
import pandas as pd
import pytest
import yaml

from fpl_model.dashboard import render_dashboard
from fpl_model.data.fpl_api import history_frame
from fpl_model.data.normalize import normalize_player_gw
from fpl_model.data.upcoming import availability_factor, build_upcoming_rows, next_gameweek
from fpl_model.pipelines import upcoming
from tests.test_normalize import raw_row
from tests.test_pipeline import POSITIONS
from tests.test_pipeline_e2e import write_season

SEASON = "2026-27"


def make_players(**overrides) -> pd.DataFrame:
    players = pd.DataFrame(
        {
            "id": range(1, len(POSITIONS) + 1),
            "first_name": "Player",
            "second_name": [str(i) for i in range(1, len(POSITIONS) + 1)],
            "web_name": [f"P{i}" for i in range(1, len(POSITIONS) + 1)],
            "team": [(i - 1) % 10 + 1 for i in range(1, len(POSITIONS) + 1)],
            "element_type": [{"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}[p] for p in POSITIONS],
            "now_cost": 50,
            "selected_by_percent": "5.0",
            "status": "a",
            "chance_of_playing_next_round": np.nan,
            "news": "",
        }
    )
    for column, value in overrides.items():
        players[column] = value
    return players


def make_fixtures(last_finished=5, events=6) -> pd.DataFrame:
    rows = []
    for event in range(1, events + 1):
        for k in range(5):  # teams (1v2), (3v4), ...
            rows.append(
                {
                    "id": event * 10 + k,
                    "event": event,
                    "team_h": 2 * k + 1,
                    "team_a": 2 * k + 2,
                    "finished": event <= last_finished,
                    "kickoff_time": "2026-09-01T14:00:00Z",
                }
            )
    return pd.DataFrame(rows)


def test_next_gameweek_is_first_unfinished():
    assert next_gameweek(make_fixtures(last_finished=5)) == 6
    with pytest.raises(ValueError):
        next_gameweek(make_fixtures(last_finished=6))


def test_availability_factor_rules():
    players = pd.DataFrame(
        {
            "status": ["a", "a", "d", "d", "i", "s", "u"],
            "chance_of_playing_next_round": [np.nan, 100, 75, np.nan, 0, np.nan, np.nan],
        }
    )
    assert availability_factor(players).tolist() == [1.0, 1.0, 0.75, 0.5, 0.0, 0.0, 0.0]


def test_upcoming_rows_cover_double_gameweeks_with_unknown_results():
    fixtures = make_fixtures()
    extra = fixtures[(fixtures["event"] == 6) & (fixtures["team_h"] == 1)].assign(id=999)
    rows = build_upcoming_rows(make_players(), pd.concat([fixtures, extra]), SEASON, 6)

    team1 = rows[rows["team_id"] == 1]
    assert team1.groupby("player_id").size().eq(2).all()  # double gameweek
    assert rows["total_points"].isna().all() and rows["minutes"].isna().all()
    assert set(rows["position"]) == {"GK", "DEF", "MID", "FWD"}
    assert rows["name"].iloc[0].startswith("Player ")


def test_api_history_flows_through_normalizer():
    history = [
        {
            "round": 3, "fixture": 21, "opponent_team": 2, "total_points": 7, "was_home": True,
            "kickoff_time": "2026-09-01T14:00:00Z", "minutes": 90, "goals_scored": 1,
            "assists": 0, "clean_sheets": 0, "goals_conceded": 1, "own_goals": 0,
            "penalties_saved": 0, "penalties_missed": 0, "yellow_cards": 0, "red_cards": 0,
            "saves": 0, "bonus": 1, "bps": 30, "influence": "20.0", "creativity": "10.0",
            "threat": "40.0", "ict_index": "7.0", "starts": 1, "expected_goals": "0.5",
            "expected_assists": "0.1", "expected_goal_involvements": "0.6",
            "expected_goals_conceded": "1.0", "value": 80, "selected": 1000,
            "transfers_balance": 0, "transfers_in": 0, "transfers_out": 0,
        }
    ]  # fmt: skip
    frame = history_frame(7, history, "Player Seven", team_id=1, element_type=3)
    result = normalize_player_gw(frame, SEASON)
    assert result.loc[0, "gameweek"] == 3 and result.loc[0, "position"] == "MID"
    assert result.loc[0, "player_id"] == 7 and result.loc[0, "total_points"] == 7
    assert history_frame(7, [], "x", 1, 3).empty


def test_dashboard_embeds_valid_json_and_escapes_script_tags():
    predictions = pd.DataFrame(
        {
            "name": ["A B"], "web_name": ["B"], "team": ["ARS"], "position": ["MID"],
            "opponent": ["CHE (H)"], "price": [8.0], "expected_points": [5.5],
            "model_points": [5.5], "availability": [1.0], "status": ["a"], "chance": [np.nan],
            "news": ["</script><b>x"], "form_5gw": [4.0], "last_gw_points": [np.nan],
        }
    )  # fmt: skip
    squad = predictions.assign(in_xi=True, captain=True, vice_captain=False, bench_order=0)
    meta = {"season": SEASON, "gameweek": 6, "history_through_gw": 5,
            "generated_at": "now", "train_rows": 10}  # fmt: skip
    html = render_dashboard(predictions, squad, meta)

    payload = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
    data = json.loads(payload.group(1))
    assert data["players"][0]["web_name"] == "B"
    assert data["players"][0]["last_gw_points"] is None
    assert data["xi"][0]["captain"] is True
    assert html.count("</script>") == 2  # the injected one was neutralised


def write_current_season(tmp_path, results_in_target_gw=False):
    raw = tmp_path / "raw" / SEASON
    raw.mkdir(parents=True)
    make_players().to_csv(raw / "players_raw.csv", index=False)
    teams = pd.DataFrame({"id": range(1, 11), "name": [f"Team {i}" for i in range(1, 11)]})
    teams["short_name"] = [f"T{i:02d}" for i in range(1, 11)]
    teams.to_csv(raw / "teams.csv", index=False)
    make_fixtures().to_csv(raw / "fixtures.csv", index=False)

    rng = np.random.default_rng(3)
    rows = []
    last_gw = 6 if results_in_target_gw else 5
    for event in range(1, last_gw + 1):
        for pid, position in enumerate(POSITIONS, start=1):
            team = (pid - 1) % 10 + 1
            rows.append(
                raw_row(
                    name=f"Player {pid}", element=pid, team=team, event=event,
                    element_type={"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}[position],
                    fixture=event * 10 + (team - 1) // 2,
                    opponent_team=team + 1 if team % 2 else team - 1, was_home=bool(team % 2),
                    total_points=99 if event == 6 else int(rng.integers(0, 9)),
                    goals_conceded=int(rng.integers(0, 3)),
                )
            )  # fmt: skip
    pd.DataFrame(rows).to_csv(raw / "merged_gw.csv", index=False)
    return raw


def make_config(tmp_path):
    config = {
        "data": {
            "raw_path": str(tmp_path / "raw"),
            "processed_path": str(tmp_path / "processed"),
            "seasons": ["2025-26", SEASON],
        },
        "model": {"random_seed": 0, "lightgbm": {"n_estimators": 10, "min_child_samples": 2}},
        "features": {"rolling_windows": [3, 5], "form_window": 5},
        "dashboard": {"output_path": str(tmp_path / "dash")},
    }
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config))
    return str(path)


def test_predict_upcoming_end_to_end(tmp_path):
    write_season(tmp_path, "2025-26", 0)
    write_current_season(tmp_path)
    config = make_config(tmp_path)

    result = upcoming.run(SEASON, None, config)
    predictions = result["predictions"]

    assert result["meta"]["gameweek"] == 6 and result["meta"]["history_through_gw"] == 5
    assert len(predictions) == len(POSITIONS) and predictions["expected_points"].ge(0).all()
    assert predictions["opponent"].str.contains(r"T\d\d \([HA]\)").all()
    assert len(result["squad"]) == 15
    assert result["path"].exists() and (tmp_path / "dash" / "latest.html").exists()


def test_target_gameweek_results_never_leak_into_its_prediction(tmp_path):
    write_season(tmp_path / "a", "2025-26", 0)
    write_season(tmp_path / "b", "2025-26", 0)
    write_current_season(tmp_path / "a", results_in_target_gw=False)
    write_current_season(tmp_path / "b", results_in_target_gw=True)  # GW6 already "played": 99 pts

    first = upcoming.run(SEASON, 6, make_config(tmp_path / "a"))["predictions"]
    second = upcoming.run(SEASON, 6, make_config(tmp_path / "b"))["predictions"]
    pd.testing.assert_series_equal(
        first.set_index("player_id")["model_points"].sort_index(),
        second.set_index("player_id")["model_points"].sort_index(),
    )


def test_injured_player_is_discounted(tmp_path):
    write_season(tmp_path, "2025-26", 0)
    raw = write_current_season(tmp_path)
    players = make_players()
    players.loc[players["id"] == 5, ["status", "chance_of_playing_next_round"]] = ["i", 0]
    players.to_csv(raw / "players_raw.csv", index=False)

    predictions = upcoming.run(SEASON, None, make_config(tmp_path))["predictions"]
    injured = predictions[predictions["player_id"] == 5].iloc[0]
    assert injured["expected_points"] == 0 and injured["model_points"] >= 0


def test_fetch_season_files_writes_pipeline_ready_files(tmp_path, monkeypatch):
    from fpl_model.data import fpl_api
    from fpl_model.data.normalize import load_historical_player_gw

    players = make_players().head(3)
    history = {
        "history": [
            {
                "round": 1, "fixture": 11, "opponent_team": 2, "total_points": 4,
                "was_home": True, "kickoff_time": "2026-08-15T14:00:00Z", "minutes": 80,
                "goals_conceded": 1, "bps": 20, "ict_index": "3.0", "starts": 1,
                "selected": 100, "value": 50,
            }
        ]
    }  # fmt: skip

    def fake_get_json(path, session=None, retries=3):
        if path.startswith("bootstrap"):
            return {
                "elements": players.to_dict("records"),
                "teams": [{"id": 1, "name": "Team 1", "short_name": "T01"}],
                "total_players": 1000,
            }
        if path.startswith("fixtures"):
            return make_fixtures().assign(stats=[[]] * 30).to_dict("records")
        return history

    monkeypatch.setattr(fpl_api, "get_json", fake_get_json)
    out = fpl_api.fetch_season_files(tmp_path / SEASON, sleep=0, progress=lambda *_: None)

    for name in ("players_raw.csv", "teams.csv", "fixtures.csv", "merged_gw.csv"):
        assert (out / name).exists()
    frame = load_historical_player_gw(out / "merged_gw.csv", SEASON, out / "teams.csv")
    assert len(frame) == 3 and frame["total_points"].eq(4).all()
