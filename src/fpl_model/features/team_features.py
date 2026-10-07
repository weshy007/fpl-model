from __future__ import annotations

import pandas as pd


def rolling_team_metric(
    frame: pd.DataFrame,
    value_column: str,
    window: int,
    team_column: str = "team_id",
) -> pd.Series:
    """Calculate a leakage-resistant rolling team metric."""
    return frame.groupby(team_column)[value_column].transform(
        lambda series: series.shift(1).rolling(window, min_periods=1).mean()
    )


def team_gameweek_form(player_fixtures: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Rolling goals for/against per team, using only *earlier* Gameweeks.

    ``player_fixtures`` is the canonical player_gw table (one row per player per
    fixture). Team goals conceded are recovered from ``goals_conceded`` (the
    maximum over a fixture's players); goals scored is the opponent's value.

    Form is computed at Gameweek level, so in a double Gameweek neither fixture
    can leak into the other's features.
    """
    team_fixture = (
        player_fixtures.groupby(
            ["season", "gameweek", "fixture_id", "team_id", "opponent_team_id"],
            as_index=False,
        )["goals_conceded"]
        .max()
        .rename(columns={"goals_conceded": "goals_against"})
    )
    opponent = team_fixture[["season", "fixture_id", "team_id", "goals_against"]].rename(
        columns={"team_id": "opponent_team_id", "goals_against": "goals_for"}
    )
    team_fixture = team_fixture.merge(
        opponent, on=["season", "fixture_id", "opponent_team_id"], how="left"
    )

    team_gw = (
        team_fixture.groupby(["season", "gameweek", "team_id"], as_index=False)[
            ["goals_for", "goals_against"]
        ]
        .mean()
        .sort_values(["season", "team_id", "gameweek"])
        .reset_index(drop=True)
    )
    for column in ("goals_for", "goals_against"):
        rolled = team_gw.groupby(["season", "team_id"])[column].transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).mean()
        )
        team_gw[f"{column}_roll{window}"] = rolled
    return team_gw.drop(columns=["goals_for", "goals_against"])
