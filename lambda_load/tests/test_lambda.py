"""Unit tests for the lambda function."""

import os

import pandas as pd
import pytest

import lambda_load
import utils.aws.s3
import utils.google

THIS_DIR = os.path.dirname(__file__)

creds = utils.google.get_creds_from_env_vars()


@pytest.fixture(name="setup_and_teardown")
def fixture_setup_and_teardown():
    """Setup and teardown palpiteiro-test."""
    pd.read_csv(os.path.join(THIS_DIR, "existing.csv"), index_col=0).to_gbq(
        destination_table="test.test",
        project_id=creds.project_id,
        if_exists="replace",
        credentials=creds,
        location="us-east4",
    )
    with open(os.path.join(THIS_DIR, "new.csv"), encoding="utf-8") as file:
        utils.aws.s3.save(file.read(), "s3://palpiteiro-test/load/test.csv")
    yield
    utils.aws.s3.delete("s3://palpiteiro-test/load")


def test_table(setup_and_teardown):  # pylint: disable=unused-argument
    """Test if it appends successfully to an existing table."""
    lambda_load.handler(
        event={
            "table": "test",
            "schema": "test",
            "uri": "s3://palpiteiro-test/load/test.csv",
            "subset": ["col1"],
        }
    )

    actual = pd.read_gbq(
        "SELECT * FROM test.test",
        project_id=creds.project_id,
        credentials=creds,
        location="us-east4",
    ).sort_values("col1", ignore_index=True)
    expected = pd.read_csv(os.path.join(THIS_DIR, "result.csv"), index_col=0)
    pd.testing.assert_frame_equal(actual.convert_dtypes(), expected.convert_dtypes())
