"""Functions for testing."""

import os
from contextlib import contextmanager

import deepdiff


def assert_jsons_are_equal(left, right, exclude_types=None):
    """Assert JSONs are equals."""
    results = deepdiff.DeepDiff(
        left,
        right,
        ignore_order=True,
        report_repetition=True,
        exclude_types=exclude_types,
    )
    assert not results, results


@contextmanager
def environ(**kwargs):
    """Set temporary environmental variables."""
    original_env = os.environ.copy()
    os.environ.update(kwargs)
    yield
    os.environ.clear()
    os.environ.update(original_env)
        

