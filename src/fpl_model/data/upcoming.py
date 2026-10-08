"""Turn next-Gameweek fixtures and player status into rows the model can score."""

from __future__ import annotations

import numpy as np
import pandas as pd

POSITION_BY_TYPE = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
UNAVAILABLE_STATUSES = {"i", "s", "u", "n"}  # injured, suspended, unavailable, not in squad


def next_gameweek(fixtures: pd.DataFrame) -> int:
    """First Gameweek that still has an unfinished fixture."""
    open_fixtures = fixtures[~fixtures["finished"].astype(bool)]
    if open_fixtures.empty:
        raise ValueError("Every fixture is finished; there is no upcoming Gameweek.")
    return int(open_fixtures["event"].min())


def availability_factor(players: pd.DataFrame) -> pd.Series:
    """Probability-style multiplier for the next round from FPL's status fields.

    Not learned from data (no historical availability feed), just FPL's own
    flags: out = 0, doubtful = the stated chance (0.5 if none), otherwise 1.
    """
    status = players["status"].astype("string").str.lower()
    chance = pd.to_numeric(players["chance_of_playing_next_round"], errors="coerce") / 100
    factor = chance.copy()
    factor[chance.isna() & (status == "d")] = 0.5
    factor[chance.isna() & (status != "d")] = 1.0
    factor[status.isin(UNAVAILABLE_STATUSES)] = 0.0
    return factor.clip(0, 1).astype("float64")


def build_upcoming_rows(
    players: pd.DataFrame,
    fixtures: pd.DataFrame,
    season: str,
    gameweek: int,
    total_players: float = 10_000_000,
) -> pd.DataFrame:
    """One row per player per fixture in ``gameweek``, with unknown results as NaN.

    ``players`` / ``fixtures`` use the official API column names
    (``first_name``, ``element_type``, ``now_cost``; ``team_h``, ``team_a``...).
    """
    games = fixtures[fixtures["event"] == gameweek]
    sides = pd.concat(
        [
            games.assign(team_id=games["team_h"], opponent_team_id=games["team_a"], was_home=True),
            games.assign(team_id=games["team_a"], opponent_team_id=games["team_h"], was_home=False),
        ]
    )[["id", "team_id", "opponent_team_id", "was_home", "kickoff_time"]]
    sides = sides.rename(columns={"id": "fixture_id"})

    base = pd.DataFrame(
        {
            "player_id": players["id"],
            "name": players["first_name"].astype(str) + " " + players["second_name"].astype(str),
            "team_id": players["team"],
            "position": players["element_type"].map(POSITION_BY_TYPE),
            "value": players["now_cost"],
            "selected": pd.to_numeric(players["selected_by_percent"], errors="coerce")
            / 100
            * total_players,
        }
    )
    rows = base.merge(sides, on="team_id", how="inner")
    rows["season"] = season
    rows["gameweek"] = gameweek
    for column in ("minutes", "total_points", "goals_conceded", "bps", "ict_index", "xgi"):
        rows[column] = np.nan
    return rows
