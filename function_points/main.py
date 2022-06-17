"""Google Cloud Functions to predict player points."""

import os

import joblib
from google.cloud import storage

# Directories
THIS_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(THIS_DIR, "model.joblib")

# Load model outside the handler for caching in between calls.
storage_client = storage.Client()
bucket = storage_client.get_bucket("matheus-experiments")
blob = bucket.blob("model.joblib")
with blob.open() as file:
    model = joblib.load(file)


def handler(request):
    """HTTP Cloud Function."""
    return model.predict(request.get_json()["calls"]).tolist()
