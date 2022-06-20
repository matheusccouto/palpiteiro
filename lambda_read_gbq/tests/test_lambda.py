"""Unit tests for the lambda function."""

import os

import pandas as pd
import pytest

import lambda_read_gbq
import utils.aws.s3
import utils.google

THIS_DIR = os.path.dirname(__file__)

creds = utils.google.get_creds_from_env_vars()


@pytest.fixture(name="expected")
def fixture_expected():
    """Setup and teardown palpiteiro-test."""
    data = pd.read_csv(os.path.join(THIS_DIR, "test.csv"), index_col=0)
    data.to_gbq(destination_table="test.test", if_exists="replace", credentials=creds)
    yield data


def test_handler(expected):  # pylint: disable=unused-argument
    """Test if it reads successfully to an existing table."""
    res = lambda_read_gbq.handler(event={"query": "SELECT * FROM test.test"})
    pd.testing.assert_frame_equal(
        pd.DataFrame.from_records(res).convert_dtypes(),
        expected.convert_dtypes(),
    )
