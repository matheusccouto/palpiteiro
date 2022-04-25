"""Unit tests for the cartola_forecast azure function."""

import json
import os

import lambda_function
from lambda_function import helper

URL = "/api/cartola_forecast"
THIS_DIR = os.path.dirname(__file__)
SAMPLES_DIR = os.path.join(THIS_DIR, "samples")


def request_with_json_body(json_path: str, method: str) -> azure.functions.HttpResponse:
    """Make a request passing JSON content as body."""
    # Read sample params.
    params = helper.read_json(json_path)

    # Construct a mock HTTP request.
    req = azure.functions.HttpRequest(
        method=method,
        body=bytes(json.dumps(params), encoding="raw_unicode_escape"),  # Encode body.
        url=URL,
        params=None,
    )

    # Call the function.
    return lambda_function.main(req)


def test_params_single():
    """Test main with with a single dict."""
    # Post request.
    body = os.path.join(SAMPLES_DIR, "params_single.json")
    resp = request_with_json_body(body, method="POST")

    # Make sure it succeed and that the predictions is reasonable.
    assert resp.status_code == 200
    pred = json.loads(resp.get_body())
    assert 0 < pred[0] < 10


def test_params_multiple():
    """Test main with with a sequence of dict."""
    # Post request.
    body = os.path.join(SAMPLES_DIR, "params_multiple.json")
    resp = request_with_json_body(body, method="POST")

    # Make sure it succeed and that the predictions is reasonable.
    assert resp.status_code == 200
    for pred in json.loads(resp.get_body()):
        assert 0 < pred < 10


def test_missing_args():
    """Test main with with missing arguments."""
    # Post request.
    body = os.path.join(SAMPLES_DIR, "params_missing.json")
    resp = request_with_json_body(body, method="POST")

    # Make sure it did not succeed.
    assert resp.status_code == 400
    assert "round, mean_prev" in resp.get_body().decode("utf-8")
