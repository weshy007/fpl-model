from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnSpec:
    """Canonical player/Gameweek column definition."""

    name: str
    dtype: str
    required: bool = True


PLAYER_GW_SCHEMA = (
    ColumnSpec("season", "string"),
    ColumnSpec("gameweek", "Int64"),
    ColumnSpec("player_id", "Int64"),
    ColumnSpec("name", "string"),
    ColumnSpec("team_id", "Int64"),
    ColumnSpec("position", "string"),
    ColumnSpec("fixture_id", "Int64"),
    ColumnSpec("opponent_team_id", "Int64"),
    ColumnSpec("was_home", "boolean"),
    ColumnSpec("kickoff_time", "datetime64[ns]", required=False),
    ColumnSpec("minutes", "Int64"),
    ColumnSpec("starts", "Int64"),
    ColumnSpec("total_points", "Int64"),
    ColumnSpec("goals_scored", "Int64"),
    ColumnSpec("assists", "Int64"),
    ColumnSpec("clean_sheets", "Int64"),
    ColumnSpec("goals_conceded", "Int64"),
    ColumnSpec("own_goals", "Int64"),
    ColumnSpec("penalties_saved", "Int64"),
    ColumnSpec("penalties_missed", "Int64"),
    ColumnSpec("saves", "Int64"),
    ColumnSpec("yellow_cards", "Int64"),
    ColumnSpec("red_cards", "Int64"),
    ColumnSpec("bonus", "Int64"),
    ColumnSpec("bps", "Int64"),
    ColumnSpec("influence", "Float64"),
    ColumnSpec("creativity", "Float64"),
    ColumnSpec("threat", "Float64"),
    ColumnSpec("ict_index", "Float64"),
    ColumnSpec("selected", "Int64"),
    ColumnSpec("transfers_balance", "Int64"),
    ColumnSpec("transfers_in", "Int64"),
    ColumnSpec("transfers_out", "Int64"),
    ColumnSpec("value", "Int64"),
    ColumnSpec("xg", "Float64", required=False),
    ColumnSpec("xa", "Float64", required=False),
    ColumnSpec("xgi", "Float64", required=False),
    ColumnSpec("xgc", "Float64", required=False),
)

PLAYER_GW_COLUMNS = tuple(spec.name for spec in PLAYER_GW_SCHEMA)
PLAYER_GW_REQUIRED_COLUMNS = tuple(
    spec.name for spec in PLAYER_GW_SCHEMA if spec.required
)

VALID_POSITIONS = frozenset({"GK", "DEF", "MID", "FWD"})

# Fields copied from the source when available. The aliases let us normalize
# both the older dataset naming and the current FPL API naming.
SOURCE_ALIASES = {
    "gameweek": ("event", "GW", "gw"),
    "player_id": ("element", "id"),
    "team_id": ("team",),
    "fixture_id": ("fixture",),
    "opponent_team_id": ("opponent_team",),
    "position": ("position", "element_type"),
    "kickoff_time": ("kickoff_time",),
    "minutes": ("minutes",),
    "starts": ("starts",),
    "total_points": ("total_points",),
    "goals_scored": ("goals_scored",),
    "assists": ("assists",),
    "clean_sheets": ("clean_sheets",),
    "goals_conceded": ("goals_conceded",),
    "own_goals": ("own_goals",),
    "penalties_saved": ("penalties_saved",),
    "penalties_missed": ("penalties_missed",),
    "saves": ("saves",),
    "yellow_cards": ("yellow_cards",),
    "red_cards": ("red_cards",),
    "bonus": ("bonus",),
    "bps": ("bps",),
    "influence": ("influence",),
    "creativity": ("creativity",),
    "threat": ("threat",),
    "ict_index": ("ict_index",),
    "selected": ("selected",),
    "transfers_balance": ("transfers_balance",),
    "transfers_in": ("transfers_in",),
    "transfers_out": ("transfers_out",),
    "value": ("value",),
    "xg": ("expected_goals", "xG", "xg"),
    "xa": ("expected_assists", "xA", "xa"),
    "xgi": ("expected_goal_involvements", "xGI", "xgi"),
    "xgc": ("expected_goals_conceded", "xGC", "xgc"),
}
