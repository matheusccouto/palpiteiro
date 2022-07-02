"""Tune machine learning model."""

import json
import logging
import os
from dataclasses import dataclass

import mlflow
import pandas as pd
import optuna
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import get_scorer
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, PowerTransformer

from . import utils

# Directories
THIS_DIR = os.path.dirname(__file__)
QUERY_TRAIN_PATH = os.path.join(THIS_DIR, "query_train.sql")
QUERY_TEST_PATH = os.path.join(THIS_DIR, "query_test.sql")
PARAMS_PATH = os.path.join(THIS_DIR, "params.json")


# MLFlows
DATABRICKS_USERNAME = os.getenv("DATABRICKS_USERNAME")
EXPERIMENT_NAME = f"/Users/{DATABRICKS_USERNAME}/palpiteiro-points"

# Model
RANDOM_STATE = 0
TARGET = "total_points"
SCORING = "neg_mean_poisson_deviance"
TEST_SIZE = 0.2
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
TIMEOUT = 15 * 60

# Read queries.
with open(QUERY_TRAIN_PATH, encoding="utf-8") as query_file:
    QUERY_TRAIN = query_file.read()

# Read queries.
with open(QUERY_TEST_PATH, encoding="utf-8") as query_file:
    QUERY_TEST = query_file.read()

# Read params.
with open(PARAMS_PATH, encoding="utf-8") as params_file:
    PARAMS = json.load(params_file)


@dataclass
class Objective:
    """Optuna objective."""

    x: pd.DataFrame  # pylint: disable=invalid-name
    y: pd.Series  # pylint: disable=invalid-name
    scoring: str
    cv: int = 5  # pylint: disable=invalid-name

    def __call__(self, trial):
        params = {
            "histgradientboostingregressor__learning_rate": trial.suggest_float(
                "histgradientboostingregressor__learning_rate", 0.001, 1, log=True
            ),
            "histgradientboostingregressor__max_iter": trial.suggest_int(
                "histgradientboostingregressor__max_iter", 10, 100, log=True
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


def tune(query_train, query_test):  # pylint: disable=invalid-name
    """Train machine learning model."""
    mlflow.set_tracking_uri("databricks")
    mlflow.set_experiment(EXPERIMENT_NAME)
    with mlflow.start_run():

        mlflow.log_artifact(__file__)

        logging.info("load data")
        mlflow.log_text(query_train, "data/sql/train.sql")
        mlflow.log_text(query_test, "data/sql/test.sql")
        x_train, y_train = utils.get_data(query_train, TARGET)
        x_test, y_test = utils.get_data(query_test, TARGET)

        logging.info("log data")
        mlflow.log_text(x_train.to_csv(index=False), "data/csv/x_train.csv")
        mlflow.log_text(y_train.to_csv(index=False), "data/csv/y_train.csv")
        mlflow.log_text(x_test.to_csv(index=False), "data/csv/x_test.csv")
        mlflow.log_text(y_test.to_csv(index=False), "data/csv/y_test.csv")

        logging.info("start tuning")
        study = optuna.create_study(direction="maximize")
        study.optimize(
            Objective(x=x_train, y=y_train, scoring=SCORING),
            n_trials=N_TRIALS,
            timeout=TIMEOUT,
        )

        logging.info("log tuning")
        mlflow.log_param("scoring", SCORING)
        mlflow.log_param("n_trials", len(study.trials))
        mlflow.log_text(str(ESTIMATOR), "model_repr.txt")
        mlflow.log_params(study.best_params)
        mlflow.log_text(json.dumps(study.best_params), "params.json")
        mlflow.log_metric(SCORING + "_valid", study.best_value)

        logging.info("evaluate model")
        ESTIMATOR.set_params(**study.best_params)
        ESTIMATOR.fit(x_train, y_train)
        score = get_scorer(SCORING)(ESTIMATOR, x_test, y_test)

        logging.info("log results")
        mlflow.log_metric(SCORING + "_test", score)


if __name__ == "__main__":
    tune(QUERY_TRAIN, QUERY_TEST)
