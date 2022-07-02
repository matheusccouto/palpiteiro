"""Google Cloud Functions to predict player points."""

import json
import os

import joblib
from google.cloud import storage

import tune
import utils

THIS_DIR = os.path.dirname(__file__)

# Google Cloud Storage
BUCKET_NAME = os.environ["BUCKET_NAME"]
MODEL_PATH = "points/model.joblib"

# Model
ESTIMATOR = tune.ESTIMATOR
PARAMS_PATH = os.path.join(THIS_DIR, "params.json")
QUERY_PATH = os.path.join(THIS_DIR, "query.sql")
TARGET = "total_points"


def handler(request):  # pylint: disable=unused-argument
    """HTTP Cloud Function handler."""
    # Read training data.
    with open(QUERY_PATH, encoding="utf-8") as query_file:
        query = query_file.read()

    # Read params
    with open(PARAMS_PATH, encoding="utf-8") as params_file:
        params = json.load(params_file)

    ESTIMATOR.set_params(**params)
    ESTIMATOR.fit(*utils.get_data(query, TARGET))

    # Upload to storage.
    blob = storage.Client().get_bucket(BUCKET_NAME).blob(MODEL_PATH)
    with blob.open(mode="wb") as model_file:
        joblib.dump(ESTIMATOR, model_file)

    return {"path": MODEL_PATH}
