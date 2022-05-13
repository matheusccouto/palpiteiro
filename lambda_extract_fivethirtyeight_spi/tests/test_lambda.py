"""Unit tests for the lambda function."""

from fnmatch import fnmatch

import pytest

import lambda_extract_fivethirtyeight_spi
import utils.aws.s3
import utils.test


def test_uri():
    """Test if lambda handler return the file URI."""
    results = lambda_extract_fivethirtyeight_spi.handler(event={})
    assert fnmatch(results["uri"], "s3://cartola-dev/spi/*-*-* *:*:*.csv")


@pytest.fixture(name="delete_atletas_mercado")
def fixture_delete_atletas_mercado():
    """Clear atletas/mercado dir from palpiteiro-test."""
    yield
    utils.aws.s3.delete("s3://palpiteiro-test/spi")


def test_exists(delete_atletas_mercado):  # pylint: disable=unused-argument
    """Test if JSON file exists."""
    with utils.test.environ(BUCKET="palpiteiro-test"):
        results = lambda_extract_fivethirtyeight_spi.handler(event={})
        assert utils.aws.s3.exists(results["uri"])