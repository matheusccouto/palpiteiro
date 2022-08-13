"""Unit tests for the lambda function."""

from fnmatch import fnmatch

import pytest

import lambda_extract_odds
import utils.aws.s3
import utils.test


def test_uri():
    """Test if lambda handler return the file URI."""
    results = lambda_extract_odds.handler(event={})
    assert fnmatch(results["uri"], "s3://palpiteiro-test/brasileirao/*-*-*T*:*:*.json")


@pytest.fixture(name="delete_odds")
def fixture_delete_odds():
    """Clear odds dir from palpiteiro-test."""
    yield
    utils.aws.s3.delete("s3://palpiteiro-test/brasileirao")


def test_exists(delete_odds):  # pylint: disable=unused-argument
    """Test if JSON file exists."""
    with utils.test.environ(BUCKET="palpiteiro-test"):
        results = lambda_extract_odds.handler(event={})
        assert utils.aws.s3.exists(results["uri"])
