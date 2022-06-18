"""Unit tests for google cloud function."""
from unittest.mock import Mock

from function_points import main


def test_handler():
    """Test function handler."""
    body = {
        "calls": [
            [0],
            [1],
            [2],
        ]
    }
    req = Mock(get_json=Mock(return_value=body))
    assert len(main.handler(req)) == 3


def test_handler():
    """Test function handler."""
    body = {"calls": [[2]]}
    req = Mock(get_json=Mock(return_value=body))
    assert main.handler(req)[0] > 0
