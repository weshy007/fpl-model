from __future__ import annotations

import pandas as pd

from .team_features import team_gameweek_form


def add_home_flag(
    frame: pd.DataFrame,
    home_team_column: str = "home_team_id",
    player_team_column: str = "team_id",
) -> pd.Series:
    """Return whether the player's team is the home team."""
    return frame[home_team_column].eq(frame[player_team_column]).astype("int8")


def add_fixture_context(player_fixtures: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Attach own-team and opponent form to each player/fixture row.

    Fixture, venue and opponent identity are known before the Gameweek starts;
    the form columns only use results from earlier Gameweeks.
    """
    form = team_gameweek_form(player_fixtures, window)
    gf, ga = f"goals_for_roll{window}", f"goals_against_roll{window}"

    own = form.rename(columns={gf: f"team_gf_roll{window}", ga: f"team_ga_roll{window}"})
    opp = form.rename(
        columns={
            "team_id": "opponent_team_id",
            gf: f"opp_gf_roll{window}",
            ga: f"opp_ga_roll{window}",
        }
    )
    out = player_fixtures.merge(own, on=["season", "gameweek", "team_id"], how="left")
    return out.merge(opp, on=["season", "gameweek", "opponent_team_id"], how="left")
