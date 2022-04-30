"""Utils HTTP functions."""

import json

import urllib3


def get(url):
    """Make a GET request without specifying any body or header."""
    return json.loads(urllib3.PoolManager().request("GET", url).data.decode("utf-8"))
