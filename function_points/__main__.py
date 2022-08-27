"""Google Cloud Functions to train model to predict player points."""

import argparse
import logging
import os

from google.cloud import storage

# Dirs
THIS_DIR = os.path.dirname(__file__)
ARTIFACT_PATH = os.path.join(THIS_DIR, "train", "{position}.joblib")

# Google Cloud Storage
BUCKET_NAME = os.environ["BUCKET_NAME"]
POSITIONS = ["goalkeeper", "defender", "fullback", "midfielder", "forward"]
MODEL_PATH = "points/{position}.joblib"


def upload():
    """Upload models artifacts to GCP."""
    bucket = storage.Client().get_bucket(BUCKET_NAME)

    # Upload to storage.
    for pos in POSITIONS:
        logging.info("Upload %s", MODEL_PATH.format(position=pos))
        blob = bucket.blob(MODEL_PATH.format(position=pos))
        blob.upload_from_filename(ARTIFACT_PATH.format(position=pos))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("func")
    args = parser.parse_args()

    if args.func == "upload":
        upload()
    else:
        raise ValueError("Invalid arg")
