from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

from .sources import HistoricalSeasonSource, OfficialFPLSource

USER_AGENT = "fpl-ai/0.1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(
    url: str,
    destination: Path,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Download one file and return provenance metadata."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    client = session or requests.Session()
    response = client.get(
        url,
        timeout=60,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    destination.write_bytes(response.content)

    return {
        "url": url,
        "path": str(destination),
        "sha256": _sha256(destination),
        "retrieved_at": datetime.now(UTC).isoformat(),
        "bytes": destination.stat().st_size,
    }


def download_historical_season(
    season: str,
    raw_root: Path,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Download the historical source files for one season."""
    source = HistoricalSeasonSource(season)
    records: list[dict[str, Any]] = []

    for filename, url in source.files.items():
        destination = raw_root / season / filename
        records.append(download_file(url, destination, session))

    return records


def download_current_season(
    season: str,
    raw_root: Path,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Snapshot the official live FPL endpoints used by the pipeline."""
    source = OfficialFPLSource()
    season_root = raw_root / season
    season_root.mkdir(parents=True, exist_ok=True)
    client = session or requests.Session()
    records: list[dict[str, Any]] = []

    for name, url in {
        "bootstrap-static.json": source.bootstrap_static,
        "fixtures.json": source.fixtures,
    }.items():
        destination = season_root / name
        records.append(download_file(url, destination, client))

    return records


def write_manifest(records: list[dict[str, Any]], destination: Path) -> None:
    """Persist retrieval provenance in deterministic JSON."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "files": records,
    }
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
