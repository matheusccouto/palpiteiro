"""Unit tests for the lambda function."""

import os

import pandas as pd
import pytest

import lambda_read_gbq
import utils.google
import utils.test

THIS_DIR = os.path.dirname(__file__)

creds = utils.google.get_creds_from_env_vars()


@pytest.fixture(name="expected", scope="module")
def fixture_expected():
    """Setup and teardown palpiteiro-test."""
    data = pd.read_csv(os.path.join(THIS_DIR, "test.csv"), index_col=0)
    data.to_gbq(destination_table="test.test_read", if_exists="replace", credentials=creds)
    yield data


def test_handler(expected):  # pylint: disable=unused-argument
    """Test if it reads successfully to an existing table."""
    res = lambda_read_gbq.handler(event={"query": "SELECT * FROM test.test_read"})
    pd.testing.assert_frame_equal(
        pd.DataFrame.from_records(res).convert_dtypes(),
        expected.convert_dtypes(),
    )


def test_return_serializable(expected):  # pylint: disable=unused-argument
    """Test if return is serializable."""
    res = lambda_read_gbq.handler(event={"query": "SELECT * FROM palpiteiro.dim_player_last"})
    print(res)
    assert utils.test.is_serializable(res)
