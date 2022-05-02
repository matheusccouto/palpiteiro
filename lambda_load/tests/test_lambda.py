"""Unit tests for the lambda function."""

import lambda_load


def test_append():
    """Test if it appends successfully to an existing table."""
    res = lambda_load.handler(
        event={
            "table": "append",
            "schema": "test",
            "uri": "s3://palpiteiro-test/test.csv",
            "subset": None,
        }
    )
    assert res["statusCode"] == 200
    assert res["message"] == "3 rows added"

