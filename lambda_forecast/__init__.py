"""Azure function to forecast Cartola FC points."""

import json
import logging
import os
from typing import Dict, List, Sequence

import joblib

from . import exceptions, helper

# Directories.
THIS_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(THIS_DIR)
MODEL_PATH = os.path.join(ROOT_DIR, "model", "model.joblib")
FEATURES_PATH = os.path.join(ROOT_DIR, "model", "features.json")


def validate_args(args: Dict[str, float], features: Sequence[str]):
    """Check for missing keys on arguments"""
    missing_args = [feat for feat in features if feat not in args]
    if missing_args:
        error_msg = f"These arguments are missing: {', '.join(missing_args)}"
        raise exceptions.MissingArgsError(error_msg)


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


def lambda_handler(event, context):  # pylint: disable=unused-argument
    """Lambda handler."""
    features = list(helper.read_json(FEATURES_PATH))  # Make sure it is a list.
    args = parse_arguments(event, features)
    model = joblib.load(MODEL_PATH)
    pred = model.predict(args)

    # Arrays are not JSON serializable.
    # It is needed to convert to a nested list before.
    return json.dumps(pred.tolist())
