"""Unit tests for the lambda function."""

from fnmatch import fnmatch

import lambda_extract_cartola_players

import utils.aws


def test_uri():
    """Test if lambda handler return the file URI."""
    results = lambda_extract_cartola_players.handler(event={})
    assert fnmatch(results["uri"], "s3://cartola-dev/atletas/mercado/20*-*.json")


def test_exists():
    """Test if JSON file exists."""
    results = lambda_extract_cartola_players.handler(event={})
    assert utils.aws.exists(results["uri"])
