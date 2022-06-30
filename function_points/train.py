"""Train machine learning model."""

import os
from dataclasses import dataclass

import joblib
import pandas as pd
import optuna
from google.cloud import storage
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, PowerTransformer

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
        (OneHotEncoder(sparse=False, handle_unknown="ignore"), (0,)),
        remainder=PowerTransformer(),
    ),
    HistGradientBoostingRegressor(
        loss="poisson",
        random_state=RANDOM_STATE,
    ),
)

# Tune
N_TRIALS = None
TIMEOUT = 60 * 60

# Read training data.
with open(QUERY_PATH, encoding="utf-8") as query_file:
    QUERY = query_file.read()


@dataclass
class Objective:
    """Optuna objective."""

    x: pd.DataFrame
    y: pd.Series

    def __call__(self, trial):
        params = {
            "histgradientboostingregressor__learning_rate": trial.suggest_float(
                "histgradientboostingregressor__learning_rate", 0.001, 1, log=True
            ),
            "histgradientboostingregressor__max_iter": trial.suggest_int(
                "histgradientboostingregressor__max_iter", 10, 1000, log=True
            ),
            "histgradientboostingregressor__max_leaf_nodes": trial.suggest_int(
                "histgradientboostingregressor__max_leaf_nodes", 16, 4096
            ),
            "histgradientboostingregressor__max_depth": trial.suggest_int(
                "histgradientboostingregressor__max_depth", 2, 256
            ),
            "histgradientboostingregressor__min_samples_leaf": trial.suggest_int(
                "histgradientboostingregressor__min_samples_leaf", 2, 512
            ),
            "histgradientboostingregressor__l2_regularization": trial.suggest_float(
                "histgradientboostingregressor__l2_regularization", 0.001, 10, log=True
            ),
            "histgradientboostingregressor__max_bins": trial.suggest_int(
                "histgradientboostingregressor__max_bins", 2, 255
            ),
        }
        ESTIMATOR.set_params(**params)
        return cross_val_score(
            ESTIMATOR,
            self.x,
            self.y,
            cv=5,
            scoring="neg_mean_poisson_deviance",
        ).mean()


def get_data(query):
    """Read and prepare training data."""
    data = pd.read_gbq(query, project_id="palpiteiro-dev")
    x = data.drop(TARGET, axis=1)  # pylint: disable=invalid-name
    y = data[TARGET]  # pylint: disable=invalid-name
    return x, y


def tune(x, y):
    """Train machine learning model."""
    study = optuna.create_study(direction="maximize")
    study.optimize(Objective(x=x, y=y), n_trials=N_TRIALS, timeout=TIMEOUT)
    return study.best_params


def train(x, y, params):
    """Train machine learning model."""
    ESTIMATOR.set_params(**params)
    ESTIMATOR.fit(x, y)

    # Upload to storage.
    blob = storage.Client().get_bucket(BUCKET_NAME).blob(MODEL_PATH)
    with blob.open(mode="wb") as model_file:
        joblib.dump(ESTIMATOR, model_file)


if __name__ == "__main__":
    x, y = get_data(QUERY)
    params = tune(x, y)
    train(x, y, params)
