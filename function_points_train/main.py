"""Google Cloud Functions to predict player points."""

import os

import joblib
from google.cloud import storage

from function_points_train.train import train

# Dirs
THIS_DIR = os.path.dirname(__file__)
QUERY_PATH = os.path.join(THIS_DIR, "query.sql")

# Google Cloud Storage
BUCKET_NAME = os.environ["BUCKET_NAME"]
MODEL_PATH = "points/model.joblib"

# Read training data.
with open(QUERY_PATH, encoding="utf-8") as query_file:
    QUERY = query_file.read()


def handler(request):  # pylint: disable=unused-argument
    """HTTP Cloud Function handler."""
    estimator = train(QUERY)

    # Upload to storage.
    blob = storage.Client().get_bucket(BUCKET_NAME).blob(MODEL_PATH)
    with blob.open(mode="wb") as model_file:
        joblib.dump(estimator, model_file)

    return {"path": MODEL_PATH}
