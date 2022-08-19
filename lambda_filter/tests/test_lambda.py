"""Unit tests for the lambda function."""

import pytest

import lambda_filter


@pytest.fixture(name="players")
def fixture_players():
    """Generate synth players data."""
    yield [
        {
            "id": 1,
            "position": "goalkeeper",
            "price": 1,
            "points": 1,
            "club": 1,
            "timestamp": "2022-01-02T01:00:00+00:00",
        },
    ] * 30 + [
        {
            "id": 1,
            "position": "goalkeeper",
            "price": 1,
            "points": 1,
            "club": 1,
            "timestamp": "2022-01-02T01:00:00-03:00",
        },
    ] * 70


def test_filter_jan_01(players):
    """Test specifying a date."""
    event = {"players": players, "date": "2022-01-01"}
    res = lambda_filter.handler(event=event, context=None)
    assert len(res["players"]) == 30


def test_filter_jan_02(players):
    """Test specifying a date."""
    event = {"players": players, "date": "2022-01-02"}
    res = lambda_filter.handler(event=event, context=None)
    assert len(res["players"]) == 70


def test_ignore_using_null(players):
    """Test setting date as null."""
    event = {"players": players, "date": None}
    res = lambda_filter.handler(event=event, context=None)
    assert len(res["players"]) == 100


def test_ignore_using_omitting(players):
    """Test omitting date."""
    event = {"players": players}
    res = lambda_filter.handler(event=event, context=None)
    assert len(res["players"]) == 100


def test_keep_params(players):
    """Test if it is able to keep the params."""
    event = {"players": players, "whatever": "else"}
    res = lambda_filter.handler(event=event, context=None)
    assert res["whatever"] == "else"
