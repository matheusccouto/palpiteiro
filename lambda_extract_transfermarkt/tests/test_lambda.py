"""Unit tests for the lambda function."""

from fnmatch import fnmatch

import lambda_extract_transfermarkt
import utils.aws.s3
import utils.test


def test_uri():
    """Test if lambda handler return the file URI."""
    results = lambda_extract_transfermarkt.handler(event={})
    assert len(results) > 1
    assert fnmatch(results[0]["uri"], "s3://palpiteiro-test/*/*.csv")


def test_exists():  # pylint: disable=unused-argument
    """Test if file exists."""
    with utils.test.environ(BUCKET="palpiteiro-test"):
        results = lambda_extract_transfermarkt.handler(event={})
        for row in results:
            assert utils.aws.s3.exists(row["uri"])
