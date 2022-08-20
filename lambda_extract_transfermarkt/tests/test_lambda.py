"""Unit tests for the lambda function."""

from fnmatch import fnmatch

import pytest

import lambda_extract_transfermarkt
import utils.aws.s3
import utils.test


@pytest.fixture(name="delete_folder")
def fixture_delete_atletas_mercado():
    """Clear transfermarkt dir from palpiteiro-test."""
    yield
    utils.aws.s3.delete("s3://palpiteiro-test/transfermarkt")


def test_uri():
    """Test if lambda handler return the file URI."""
    results = lambda_extract_transfermarkt.handler(event={})
    assert len(results) > 1
    assert fnmatch(results[0]["uri"], "s3://palpiteiro-test/transfermarkt/*/*.csv")


def test_exists(delete_folder):  # pylint: disable=unused-argument
    """Test if file exists."""
    with utils.test.environ(BUCKET="palpiteiro-test"):
        results = lambda_extract_transfermarkt.handler(event={})
        for row in results:
            assert utils.aws.s3.exists(row["uri"])
