"""Train machine learning model."""

import os

import joblib
import pandas as pd
from google.cloud import storage
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, PowerTransformer

# import utils.google

# Directories
THIS_DIR = os.path.dirname(__file__)
QUERY_PATH = os.path.join(THIS_DIR, "query.sql")

# Google Cloud Storage
BUCKET_NAME = os.environ["BUCKET_NAME"]
MODEL_PATH = "points/model.joblib"

# Model
RANDOM_STATE = 0
TARGET = "total_points"
ESTIMATOR = make_pipeline(
    make_column_transformer(
        (OneHotEncoder(sparse=False), (0,)),
        remainder=PowerTransformer(),
    ),
    HistGradientBoostingRegressor(
        loss="poisson",
        random_state=RANDOM_STATE,
    ),
)

# Read training data.
with open(QUERY_PATH, encoding="utf-8") as query_file:
    QUERY = query_file.read()


def train(query):
    """Train machine learning model."""
    # Read and prepare training data.
    data = pd.read_gbq(query)
    x = data.drop(TARGET, axis=1)  # pylint: disable=invalid-name
    y = data[TARGET]  # pylint: disable=invalid-name

    # Train and persist model.
    ESTIMATOR.fit(x, y)

    # Upload to storage.
    blob = storage.Client().get_bucket(BUCKET_NAME).blob(MODEL_PATH)
    with blob.open(mode="wb") as model_file:
        joblib.dump(ESTIMATOR, model_file)


if __name__ == "__main__":
    train(QUERY)
