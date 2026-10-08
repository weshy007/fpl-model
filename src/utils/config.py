from __future__ import annotations

from pathlib import Path

import yaml

DEFAULT_CONFIG = Path("configs/config.yaml")


def load_yaml(path: str | Path) -> dict:
    """Load a YAML configuration file."""
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict:
    """Load the project configuration."""
    return load_yaml(path)
