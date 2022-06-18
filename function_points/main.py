"""Google Cloud Functions to predict player points."""

import os

import joblib
from google.cloud import storage

BUCKET_NAME = os.environ["BUCKET_NAME"]
MODEL_PATH = "points/model.joblib"

# Load model outside the handler for caching in between calls.
blob = storage.Client().get_bucket(BUCKET_NAME).blob(MODEL_PATH)
with blob.open(mode="rb") as file:
    model = joblib.load(file)


def handler(request):
    """HTTP Cloud Function."""
    return model.predict(request.get_json()["calls"]).tolist()
