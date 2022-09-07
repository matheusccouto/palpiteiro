"""Unit tests for google cloud function."""

import os
from unittest.mock import Mock

import pandas as pd
import pytest

import utils.test

# function_points will access env vars during import.
with utils.test.environ(BUCKET_NAME="palpiteiro-dev"):
    from function_points import main

THIS_DIR = os.path.dirname(__file__)
SAMPLE_PATH = os.path.join(THIS_DIR, "sample.csv")


@pytest.fixture(name="req")
def request_fixture():
    """Sample data for testing."""
    body = {
        "calls": pd.read_csv(SAMPLE_PATH).values.tolist(),
        "userDefinedContext": {
            "names": [
                "position",
                "total_points_last_5_at",
                "offensive_points_last_5_at",
                "defensive_points_last_5_at",
                "spi_club",
                "spi_opponent",
                "prob_club",
                "prob_opponent",
                "prob_tie",
                "importance_club",
                "importance_opponent",
                "proj_score_club",
                "proj_score_opponent",
                "total_points_club_last_5_at",
                "offensive_points_club_last_5_at",
                "defensive_points_club_last_5_at",
                "total_allowed_points_opponent_last_5_at",
                "offensive_allowed_points_opponent_last_5_at",
                "defensive_allowed_points_opponent_last_5_at",
                "played_last_5",
                "avg_odds_club",
                "avg_odds_opponent",
                "avg_odds_draw",
            ]
        },
    }
    return Mock(get_json=Mock(return_value=body))


def test_count(req):
    """Test function handler."""
    assert len(main.handler(req)["replies"]) == 201


def test_values(req):
    """Test function handler."""
    values = main.handler(req)["replies"]
    assert max(values) < 20
    assert min(values) > -20
