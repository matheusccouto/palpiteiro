"""Unit tests for google cloud function."""

import os
from unittest.mock import Mock

import joblib
import pytest
from google.cloud import storage

import utils.test

# function_points will access env vars during import.
with utils.test.environ(BUCKET_NAME="palpiteiro-test"):
    from function_points_train import main

THIS_DIR = os.path.dirname(__file__)


@pytest.fixture(name="req")
def request_fixture():
    """Sample data for testing."""
    body = {"timeout": 1, "n_trials": 1}
    return Mock(get_json=Mock(return_value=body))


@pytest.fixture(name="clear_bucket")
def request_clear_bucket():
    """Sample data for testing."""
    blob = storage.Client().get_bucket("palpiteiro-test").blob(main.MODEL_PATH)
    if blob.exists():
        blob.delete()


def test_predict(req, clear_bucket):  # pylint: disable=unused-argument
    """Test if the saved model has the predict method.."""
    main.handler(req)
    client = storage.Client()
    blob = client.get_bucket("palpiteiro-test").blob(main.MODEL_PATH)
    with blob.open(mode="rb") as file:
        model = joblib.load(file)
    assert hasattr(model, "predict")
