"""Unit tests for the lambda function."""

import datetime

import lambda_extract_cartola_players
import utils.test


def test_handler():
    """Test lambda handler."""
    results = lambda_extract_cartola_players.handler(event={}, context={})
    expected = {"clubes": None, "posicoes": None, "status": None, "atletas": None}
    utils.test.assert_jsons_are_equal(
        left=results,
        right=expected,
        exclude_types=[type(None)],
    )


def test_season():
    """Test if season is inside atletas key."""
    results = lambda_extract_cartola_players.handler(event={}, context={})
    for player in results["atletas"]:
        assert player["temporada_id"] == datetime.datetime.today().year
