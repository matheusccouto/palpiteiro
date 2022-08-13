"""Utils HTTP functions."""

import json

import urllib3


def get(url, params=None, body=None, headers=None, parse_json=True):
    """Make a GET request."""
    if body is None:
        body = {}

    if headers is None:
        headers = {}

    if params is None:
        params = {}

    res = (
        urllib3.PoolManager()
        .request("GET", url, fields=params, headers=headers, body=json.dumps(body))
        .data.decode("utf-8")
    )
    return json.loads(res) if parse_json else res


def post(url, body=None, headers=None, parse_json=True):
    """Make a POST request."""
    if body is None:
        body = {}

    if headers is None:
        headers = {}

    res = (
        urllib3.PoolManager()
        .request(method="POST", url=url, headers=headers, body=json.dumps(body))
        .data.decode("utf-8")
    )
    return json.loads(res) if parse_json else res
