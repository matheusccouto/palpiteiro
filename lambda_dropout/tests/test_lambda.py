"""Unit tests for the lambda function."""

import pytest

import lambda_dropout


@pytest.fixture(name="players")
def fixture_delete_partidas():
    """Clear partida dir from palpiteiro-test."""
    yield [
        {"id": 1, "position": "goalkeeper", "price": 1, "points": 1, "club": 1},
    ] * 100


def test_droupout(players):
    """Test if JSON file exists."""
    for val in [0.1, 0.5, 1.0]:
        event = {"players": players, "dropout": val}
        res = lambda_dropout.handler(event=event, context=None)
        assert len(res) == len(players) * val