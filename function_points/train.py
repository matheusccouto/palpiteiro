"""Train machine learning model."""

import os

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

import utils.google

# Directories
THIS_DIR = os.path.dirname(__file__)
QUERY_PATH = os.path.join(THIS_DIR, "query.sql")
MODEL_PATH = os.path.join(THIS_DIR, "model.joblib")

# Google Cloud
LOCATION = "us-east4"
CREDS = utils.google.get_creds_from_env_vars()

# Model
RANDOM_STATE = 0
ESTIMATOR = HistGradientBoostingRegressor(random_state=RANDOM_STATE)
TARGET = "total_points"

# Read training data.
with open(QUERY_PATH, encoding="utf-8") as file:
    QUERY = file.read()


def train(query, creds):
    """Train machine learning model."""
    data = pd.read_gbq(query, credentials=creds)
    x = data.drop(TARGET, axis=1)
    y = data[TARGET]
    ESTIMATOR.fit(x, y)
    joblib.dump(ESTIMATOR, MODEL_PATH)

if __name__ == "__main__":
    train(QUERY, CREDS)
