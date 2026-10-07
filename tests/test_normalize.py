import pandas as pd
import pytest

from fpl_model.data.normalize import load_historical_player_gw, normalize_player_gw
from fpl_model.data.validation import validate_player_gw


def raw_row(**overrides):
    row = {
        "name": "Player One",
        "team": 1,
        "element": 101,
        "event": 3,
        "total_points": 8,
        "minutes": 90,
        "element_type": 3,
        "fixture": 44,
        "opponent_team": 2,
        "was_home": True,
        "starts": 1,
        "goals_scored": 1,
        "assists": 0,
        "clean_sheets": 1,
        "goals_conceded": 0,
        "own_goals": 0,
        "penalties_saved": 0,
        "penalties_missed": 0,
        "saves": 0,
        "yellow_cards": 0,
        "red_cards": 0,
        "bonus": 2,
        "bps": 38,
        "influence": "24.0",
        "creativity": "18.5",
        "threat": "42.0",
        "ict_index": "8.4",
        "selected": 10000,
        "transfers_balance": 250,
        "transfers_in": 300,
        "transfers_out": 50,
        "value": 75,
        "expected_goals": "0.52",
        "expected_assists": "0.13",
        "expected_goal_involvements": "0.65",
        "expected_goals_conceded": "0.80",
        "kickoff_time": "2025-08-16T14:00:00Z",
    }
    row.update(overrides)
    return row


def test_load_historical_player_gw(tmp_path):
    path = tmp_path / "merged_gw.csv"
    pd.DataFrame([raw_row()]).to_csv(path, index=False)

    frame = load_historical_player_gw(path, "2025-26")

    assert frame.loc[0, "season"] == "2025-26"
    assert frame.loc[0, "player_id"] == 101
    assert frame.loc[0, "gameweek"] == 3
    assert frame.loc[0, "position"] == "MID"
    assert frame.loc[0, "team_id"] == 1
    assert frame.loc[0, "fixture_id"] == 44
    assert frame.loc[0, "xg"] == pytest.approx(0.52)
    assert frame.loc[0, "xa"] == pytest.approx(0.13)


def test_normalized_schema_has_stable_columns():
    frame = normalize_player_gw(pd.DataFrame([raw_row()]), "2025-26")

    expected = {
        "season",
        "gameweek",
        "player_id",
        "name",
        "team_id",
        "position",
        "fixture_id",
        "opponent_team_id",
        "was_home",
        "kickoff_time",
        "minutes",
        "starts",
        "total_points",
        "goals_scored",
        "assists",
        "clean_sheets",
        "goals_conceded",
        "own_goals",
        "penalties_saved",
        "penalties_missed",
        "saves",
        "yellow_cards",
        "red_cards",
        "bonus",
        "bps",
        "influence",
        "creativity",
        "threat",
        "ict_index",
        "selected",
        "transfers_balance",
        "transfers_in",
        "transfers_out",
        "value",
        "xg",
        "xa",
        "xgi",
        "xgc",
    }

    assert set(frame.columns) == expected
    assert frame.shape == (1, len(expected))


def test_optional_expected_stats_are_nan_when_source_lacks_them():
    row = raw_row()
    row.pop("expected_goals")
    row.pop("expected_assists")
    row.pop("expected_goal_involvements")
    row.pop("expected_goals_conceded")

    frame = normalize_player_gw(pd.DataFrame([row]), "2018-19")

    assert frame["xg"].isna().all()
    assert frame["xa"].isna().all()
    assert frame["xgi"].isna().all()
    assert frame["xgc"].isna().all()


def test_missing_required_source_column_fails():
    row = raw_row()
    row.pop("minutes")

    with pytest.raises(ValueError, match="minutes"):
        normalize_player_gw(pd.DataFrame([row]), "2025-26")


def test_invalid_position_fails():
    with pytest.raises(ValueError, match="Invalid source position"):
        normalize_player_gw(pd.DataFrame([raw_row(element_type=9)]), "2025-26")


def test_duplicate_player_gameweek_fails():
    frame = pd.DataFrame([raw_row(), raw_row(element=101, name="Player One")])

    with pytest.raises(ValueError, match="Duplicate key rows"):
        normalize_player_gw(frame, "2025-26")


def test_gameweek_must_be_1_to_38():
    with pytest.raises(ValueError, match="between 1 and 38"):
        normalize_player_gw(pd.DataFrame([raw_row(event=39)]), "2025-26")


def test_negative_minutes_fails():
    with pytest.raises(ValueError, match="minutes.*negative"):
        normalize_player_gw(pd.DataFrame([raw_row(minutes=-1)]), "2025-26")


def test_schema_validator_rejects_duplicate_key():
    frame = normalize_player_gw(pd.DataFrame([raw_row()]), "2025-26")
    duplicate = pd.concat([frame, frame], ignore_index=True)

    with pytest.raises(ValueError, match="Duplicate key rows"):
        validate_player_gw(duplicate)


def test_double_gameweek_is_valid():
    frame = pd.DataFrame([raw_row(fixture=44), raw_row(fixture=45, opponent_team=3)])
    result = normalize_player_gw(frame, "2025-26")
    assert len(result) == 2


def test_negative_points_are_valid():
    result = normalize_player_gw(pd.DataFrame([raw_row(total_points=-3)]), "2025-26")
    assert result.loc[0, "total_points"] == -3


def test_gkp_alias_and_non_player_rows():
    frame = pd.DataFrame(
        [
            raw_row(position="GKP", element_type=None),
            raw_row(position="AM", element=999, element_type=None, name="Manager"),
        ]
    ).drop(columns="element_type")
    result = normalize_player_gw(frame, "2025-26")
    assert result["position"].tolist() == ["GK"]


def test_team_names_are_mapped_with_lookup():
    frame = pd.DataFrame([raw_row(team="Arsenal")])
    result = normalize_player_gw(frame, "2025-26", team_ids={"Arsenal": 1})
    assert result.loc[0, "team_id"] == 1
