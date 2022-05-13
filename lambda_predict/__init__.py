"""Lambda function to forecast Cartola FC points."""

import os
from typing import Dict, List, Sequence

import joblib

import utils

# Directories.
THIS_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(THIS_DIR)
MODEL_PATH = os.path.join(THIS_DIR, "model", "model.joblib")
FEATURES_PATH = os.path.join(THIS_DIR, "model", "features.json")


def validate_args(args: Dict[str, float], features: Sequence[str]):
    """Check for missing keys on arguments"""
    missing_args = [feat for feat in features if feat not in args]
    if missing_args:
        error_msg = f"These arguments are missing: {', '.join(missing_args)}"
        raise ValueError(error_msg)


def parse_args_dict(args: Dict[str, float], features: Sequence[str]) -> List[float]:
    """Parse args from an individual dict into model's format."""
    validate_args(args, features)
    # If it didn't raise, construct the arguments sequence.
    return [args[feat] for feat in features]


def parse_args_dict_sequence(
    args: Sequence[Dict[str, float]],
    features: Sequence[str],
) -> List[List[float]]:
    """Parse arguments from a JSON sequence to the model's format."""
    return [parse_args_dict(arg, features) for arg in args]


def parse_arguments(
    event: dict,
    features: Sequence[str],
) -> List[List[float]]:
    """Parse arguments from request."""
    return parse_args_dict_sequence(event, features)


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    features = list(utils.read_json(FEATURES_PATH))  # Make sure it is a list.
    args = parse_arguments(event, features)
    model = joblib.load(MODEL_PATH)
    return model.predict(args).tolist()
