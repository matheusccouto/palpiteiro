"""Helper functions for unit-tests."""

import json
import os
from typing import Any, Dict, List

THIS_FOLDER = os.path.dirname(__file__)
PLAYERS_JSON_PATH = os.path.join(THIS_FOLDER, "sample.json")
POSITIONS = ["goalkeeper", "fullback", "defender", "midfielder", "forward", "coach"]


def load_players_dict() -> List[Dict[str, Any]]:
    """Create line-up players dict."""
    # Load players data from JSON folder.
    with open(PLAYERS_JSON_PATH, mode="r", encoding="utf-8") as file:
        return json.load(file)
