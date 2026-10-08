import json
from pathlib import Path

from src.data.download import write_manifest


def test_write_manifest(tmp_path: Path):
    destination = tmp_path / "manifest.json"
    write_manifest(
        [{"url": "https://example.com/a.csv", "path": "a.csv", "sha256": "abc"}],
        destination,
    )

    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["files"][0]["sha256"] == "abc"
    assert "generated_at" in payload
