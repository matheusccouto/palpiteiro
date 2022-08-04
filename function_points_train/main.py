"""Google Cloud Functions to train model to predict player points."""

import os

import joblib
import pandas as pd
import skdict
import yaml
from google.cloud import storage

# Dirs
THIS_DIR = os.path.dirname(__file__)

# Google Cloud Storage
BUCKET_NAME = os.environ["BUCKET_NAME"]
MODEL_PATH = "points/model.joblib"

# Model
ESTIMATOR = os.path.join(THIS_DIR, "estimator.yml")
QUERY_PATH = os.path.join(THIS_DIR, "query.sql")
TARGET = "total_points"
INDEX = "id"


def get_data(path, target, index_col):
    """Read and prepare training data."""
    # pylint: disable=invalid-name
    with open(path, encoding="utf-8") as file:
        data = pd.read_gbq(file.read(), index_col=index_col)
    return data.drop(target, axis=1), data[target]


def get_estimator(path):
    """Get estimator."""
    with open(path, encoding="utf-8") as file:
        return skdict.load(yaml.safe_load(file))


def handler(request):  # pylint: disable=unused-argument
    """HTTP Cloud Function handler."""
    # Load artifacts and train model.
    data = get_data(QUERY_PATH, TARGET, INDEX)
    estimator = get_estimator(ESTIMATOR)
    estimator.fit(*data)

    # Upload to storage.
    blob = storage.Client().get_bucket(BUCKET_NAME).blob(MODEL_PATH)
    with blob.open(mode="wb") as file:
        joblib.dump(estimator, file)

    return {"path": MODEL_PATH}
