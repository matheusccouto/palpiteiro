"""Tune machine learning model."""

import logging
import os
from dataclasses import dataclass

# import mlflow
import pandas as pd
import optuna
import skyaml
from sklearn.base import BaseEstimator
from sklearn.metrics import get_scorer
from sklearn.model_selection import cross_val_score

# Dirs
THIS_DIR = os.path.dirname(__file__)

# MLFlows
DATABRICKS_USERNAME = os.getenv("DATABRICKS_USERNAME")
EXPERIMENT_NAME = f"/Users/{DATABRICKS_USERNAME}/palpiteiro-points"


@dataclass
class Objective:
    """Optuna objective."""

    pipeline: BaseEstimator
    x: pd.DataFrame  # pylint: disable=invalid-name
    y: pd.Series  # pylint: disable=invalid-name
    metric: str
    cv: int  # pylint: disable=invalid-name

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
        self.pipeline.set_params(**params)
        return cross_val_score(
            self.pipeline,
            self.x,
            self.y,
            cv=self.cv,
            scoring=self.metric,
        ).mean()


def get_data(query, target):
    """Read and prepare training data."""
    data = pd.read_gbq(query)
    x = data.drop(target, axis=1)  # pylint: disable=invalid-name
    y = data[target]  # pylint: disable=invalid-name
    return x, y


def tune(pipeline, query_train, query_test, target, metric, n_trials, timeout, output):
    """Train machine learning model."""
    # mlflow.set_tracking_uri("databricks")
    # mlflow.set_experiment(EXPERIMENT_NAME)
    # with mlflow.start_run():

    #     mlflow.log_artifact(__file__)

    logging.info("load pipeline")
    pipe = skyaml.yaml2py(pipeline)
    # mlflow.log_artifact(pipeline, "pipeline-in.yml")

    logging.info("load data")
    # mlflow.log_artifact(query_train, "data/sql/train.sql")
    # mlflow.log_artifact(query_test, "data/sql/test.sql")
    with open(query_train, encoding="utf-8") as f:
        x_train, y_train = get_data(f.read(), target)
    with open(query_test, encoding="utf-8") as f:
        x_test, y_test = get_data(f.read(), target)

    logging.info("log data")
    # mlflow.log_param("target", target)
    # mlflow.log_text(x_train.to_csv(index=False), "data/csv/x_train.csv")
    # mlflow.log_text(y_train.to_csv(index=False), "data/csv/y_train.csv")
    # mlflow.log_text(x_test.to_csv(index=False), "data/csv/x_test.csv")
    # mlflow.log_text(y_test.to_csv(index=False), "data/csv/y_test.csv")

    logging.info("start tuning")
    study = optuna.create_study(direction="maximize")
    study.optimize(
        Objective(pipeline=pipe, x=x_train, y=y_train, metric=metric, cv=5),
        n_trials=n_trials,
        timeout=timeout,
    )

    logging.info("log tuning")
    # mlflow.log_param("metric", metric)
    # mlflow.log_param("n_trials", len(study.trials))
    # mlflow.log_params(study.best_params)
    # mlflow.log_metric(metric + "_valid", study.best_value)

    logging.info("evaluate model")
    pipe.set_params(**study.best_params)
    pipe.fit(x_train, y_train)
    score = get_scorer(metric)(pipe, x_test, y_test)

    logging.info("export model yaml")
    skyaml.py2yaml(pipe, output)
    # mlflow.log_artifact(output, "pipeline-out.yml")

    logging.info("log results")
    # mlflow.log_metric(metric + "_test", score)
