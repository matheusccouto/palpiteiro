"""Train machine learning model."""

import os

import pandas as pd
from sklearn import metrics
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, PowerTransformer

import utils.google

RANDOM_STATE = 0

# Directories
THIS_DIR = os.path.dirname(__file__)
QUERY_PATH = os.path.join(THIS_DIR, "query.sql")

# Google Cloud
LOCATION = "us-east4"
CREDS = utils.google.get_creds_from_env_vars()

# Model
ESTIMATOR = make_pipeline(
    make_column_transformer(
        (OneHotEncoder(sparse=False), (0,)),
        remainder=PowerTransformer(),
    ),
    HistGradientBoostingRegressor(random_state=RANDOM_STATE),
)

# Read training data.
with open(QUERY_PATH, encoding="utf-8") as file:
    query = file.read()
data = pd.read_gbq(query, credentials=CREDS)

def handler(event, context):
    """Lambda handler."""

