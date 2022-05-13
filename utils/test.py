"""Functions for testing."""

import os
from contextlib import contextmanager


@contextmanager
def environ(**kwargs):
    """Set temporary environmental variables."""
    original_env = os.environ.copy()
    os.environ.update(kwargs)
    yield
    os.environ.clear()
    os.environ.update(original_env)
        

