"""Google Cloud Functions to predict player points."""

import os

import joblib

# Directories
THIS_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(THIS_DIR, "model.joblib")

# Load model outside the handler for caching in between calls.
model = joblib.load(MODEL_PATH)


def handler(request):
    """HTTP Cloud Function."""
    return model.predict(request.get_json()).tolist()
