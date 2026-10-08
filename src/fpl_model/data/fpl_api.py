"""Minimal client for the official Fantasy Premier League API.

It writes the same raw files (``players_raw.csv``, ``teams.csv``,
``fixtures.csv``, ``merged_gw.csv``) that the community dataset provides, so
the rest of the pipeline does not care where the data came from.
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "fpl-model research project (github.com/weshy007/fpl-model)"}

# element-summary history fields that the normalizer understands
HISTORY_COLUMNS = [
    "element", "fixture", "opponent_team", "total_points", "was_home", "kickoff_time",
    "minutes", "goals_scored", "assists", "clean_sheets", "goals_conceded", "own_goals",
    "penalties_saved", "penalties_missed", "yellow_cards", "red_cards", "saves", "bonus",
    "bps", "influence", "creativity", "threat", "ict_index", "starts", "expected_goals",
    "expected_assists", "expected_goal_involvements", "expected_goals_conceded", "value",
    "selected", "transfers_balance", "transfers_in", "transfers_out",
]  # fmt: skip


def get_json(path: str, session: requests.Session | None = None, retries: int = 3):
    """GET ``BASE_URL/path`` and return parsed JSON, retrying transient errors."""
    client = session or requests
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = client.get(f"{BASE_URL}/{path}", headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as error:
            last_error = error
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"FPL API request failed for {path!r}: {last_error}")


def history_frame(
    element_id: int, history: list[dict], name: str, team_id: int, element_type: int
) -> pd.DataFrame:
    """Convert one player's ``element-summary`` history to merged_gw-style rows."""
    if not history:
        return pd.DataFrame()
    frame = pd.DataFrame(history)
    frame["element"] = element_id
    frame["GW"] = frame["round"]
    frame["name"] = name
    frame["team"] = team_id
    frame["element_type"] = element_type
    keep = ["name", "team", "element_type", "GW"] + [
        c for c in HISTORY_COLUMNS if c in frame.columns
    ]
    return frame[keep]


def fetch_season_files(season_dir: str | Path, sleep: float = 0.1, progress=print) -> Path:
    """Download players, teams, fixtures and every player's gameweek history."""
    out = Path(season_dir)
    out.mkdir(parents=True, exist_ok=True)
    with requests.Session() as session:
        bootstrap = get_json("bootstrap-static/", session)
        elements = pd.DataFrame(bootstrap["elements"])
        teams = pd.DataFrame(bootstrap["teams"])
        fixtures = pd.DataFrame(get_json("fixtures/", session))

        elements.to_csv(out / "players_raw.csv", index=False)
        teams.to_csv(out / "teams.csv", index=False)
        fixtures.drop(columns=["stats"], errors="ignore").to_csv(out / "fixtures.csv", index=False)
        (out / "total_players.txt").write_text(str(bootstrap.get("total_players", "")))

        frames = []
        for i, row in enumerate(elements.itertuples(), start=1):
            summary = get_json(f"element-summary/{row.id}/", session)
            name = f"{row.first_name} {row.second_name}"
            frames.append(
                history_frame(row.id, summary.get("history", []), name, row.team, row.element_type)
            )
            if i % 100 == 0:
                progress(f"  fetched history for {i}/{len(elements)} players")
            time.sleep(sleep)
    pd.concat([f for f in frames if not f.empty], ignore_index=True).to_csv(
        out / "merged_gw.csv", index=False
    )
    return out
