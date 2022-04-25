"""Helper functions."""

import json


def read_json(path: str) -> dict:
    """Read JSON from file path."""
    with open(path, mode="r", encoding="utf-8") as file:
        return json.load(file)
