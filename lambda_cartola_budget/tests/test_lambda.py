"""Unit tests for the lambda function."""

import lambda_cartola_budget


def test_handler():
    """Test if returns an existing value."""
    res = lambda_cartola_budget.handler(event=None, context=None)
    assert 0 < res["budget"] < 250
