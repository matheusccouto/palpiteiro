"""Helper functions."""

import pandas as pd


def get_data(query, target):
    """Read and prepare training data."""
    data = pd.read_gbq(query)
    x = data.drop(target, axis=1)  # pylint: disable=invalid-name
    y = data[target]  # pylint: disable=invalid-name
    return x, y
