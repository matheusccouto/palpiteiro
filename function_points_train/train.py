"""Train machine learning model."""

import json
import os
from dataclasses import dataclass

import pandas as pd
import optuna
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, PowerTransformer

# Directories
THIS_DIR = os.path.dirname(__file__)
QUERY_PATH = os.path.join(THIS_DIR, "query.sql")
PARAMS_PATH = os.path.join(THIS_DIR, "params.json")

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

# Read query.
with open(QUERY_PATH, encoding="utf-8") as query_file:
    QUERY = query_file.read()

# Read params.
with open(PARAMS_PATH, encoding="utf-8") as params_file:
    PARAMS = json.load(params_file)


@dataclass
class Objective:
    """Optuna objective."""

    x: pd.DataFrame  # pylint: disable=invalid-name
    y: pd.Series  # pylint: disable=invalid-name
    cv: int = 5  # pylint: disable=invalid-name
    scoring: str = "neg_mean_poisson_deviance"

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
            cv=self.cv,
            scoring=self.scoring,
        ).mean()


def get_data(query):
    """Read and prepare training data."""
    data = pd.read_gbq(query, project_id="palpiteiro-dev")
    x = data.drop(TARGET, axis=1)  # pylint: disable=invalid-name
    y = data[TARGET]  # pylint: disable=invalid-name
    return x, y


def tune(x, y):  # pylint: disable=invalid-name
    """Train machine learning model."""
    study = optuna.create_study(direction="maximize")
    study.optimize(Objective(x=x, y=y), n_trials=N_TRIALS, timeout=TIMEOUT)
    return study.best_params


def train(query):
    """Train machine learning model."""
    x, y = get_data(query)  # pylint: disable=invalid-name
    ESTIMATOR.set_params(**PARAMS)
    ESTIMATOR.fit(x, y)
    return ESTIMATOR


def main(query):
    """Train machine learning model."""
    x, y = get_data(query)  # pylint: disable=invalid-name
    params = tune(x, y)


if __name__ == "__main__":
    main(QUERY)
