"""Google Cloud Functions to predict player points."""

import os

import joblib
from google.cloud import storage

BUCKET_NAME = os.environ["BUCKET_NAME"]
POSITIONS = ["goalkeeper", "defender", "fullback", "midfielder", "forward"]
MODEL_PATH = "points/{position}.joblib"

bucket = storage.Client().get_bucket(BUCKET_NAME)


def load(path,):
    """Load model with joblib."""
    blob = bucket.blob(path)
    with blob.open(mode="rb") as file:
        return joblib.load(file)


# Load models outside the handler for caching in between calls.
models = {p: load(MODEL_PATH.format(position=p)) for p in POSITIONS}


def handler(request):
    """HTTP Cloud Function handler."""
    data = request.get_json()["calls"]
    pred = [models[row[0]].predict([row[1:]])[0] for row in data]
    return {"replies": pred}
