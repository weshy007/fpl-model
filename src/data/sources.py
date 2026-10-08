from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HistoricalSeasonSource:
    """Raw URLs for one historical FPL season."""

    season: str

    @property
    def base_url(self) -> str:
        return (
            "https://raw.githubusercontent.com/vaastav/"
            f"Fantasy-Premier-League/master/data/{self.season}"
        )

    @property
    def files(self) -> dict[str, str]:
        return {
            "merged_gw.csv": f"{self.base_url}/gws/merged_gw.csv",
            "fixtures.csv": f"{self.base_url}/fixtures.csv",
            "teams.csv": f"{self.base_url}/teams.csv",
            "players_raw.csv": f"{self.base_url}/players_raw.csv",
        }


@dataclass(frozen=True)
class OfficialFPLSource:
    """Endpoints used for the live/current season."""

    base_url: str = "https://fantasy.premierleague.com/api"

    @property
    def bootstrap_static(self) -> str:
        return f"{self.base_url}/bootstrap-static/"

    @property
    def fixtures(self) -> str:
        return f"{self.base_url}/fixtures/"

    def element_summary(self, player_id: int) -> str:
        return f"{self.base_url}/element-summary/{player_id}/"
