import pandas as pd

from fpl_ai.data.normalize import load_historical_player_gw


def test_load_historical_player_gw(tmp_path):
    path = tmp_path / "merged_gw.csv"
    pd.DataFrame(
        {
            "name": ["Player One"],
            "team": [1],
            "element": [101],
            "event": [3],
            "total_points": [8],
            "minutes": [90],
            "element_type": [3],
        }
    ).to_csv(path, index=False)

    frame = load_historical_player_gw(path, "2025-26")

    assert frame.loc[0, "season"] == "2025-26"
    assert frame.loc[0, "player_id"] == 101
    assert frame.loc[0, "gameweek"] == 3
    assert frame.loc[0, "position"] == "MID"
