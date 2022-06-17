"""Unit tests for the lambda function."""

import os

import pytest

import lambda_predict
import utils

THIS_DIR = os.path.dirname(__file__)
SAMPLES_DIR = os.path.join(THIS_DIR, "samples")


def test_params_single():
    """Test main with with a single dict."""
    body = utils.read_json(os.path.join(SAMPLES_DIR, "params_single.json"))
    res = lambda_predict.handler(event=body)
    assert 0 < res[0] < 10


def test_params_multiple():
    """Test main with with a sequence of dict."""
    body = utils.read_json(os.path.join(SAMPLES_DIR, "params_multiple.json"))
    res = lambda_predict.handler(event=body)
    for pred in res:
        assert 0 < pred < 10


def test_missing_args():
    """Test main with with missing arguments."""
    body = utils.read_json(os.path.join(SAMPLES_DIR, "params_missing.json"))
    with pytest.raises(ValueError):
        lambda_predict.handler(event=body)