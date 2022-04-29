"""Functions for testing."""

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
