"""Train machine learning model."""

import json
import logging
import os
import sys
import warnings
from dataclasses import dataclass
from typing import Callable

import joblib
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd
import requests
from sklearn import metrics
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, PowerTransformer
from sqlalchemy import create_engine

# Params
LOG_LEVEL = "INFO"
RANDOM_STATE = 1902
N_TRIALS = 1
TIMEOUT = None

# Metrics
SCORINGS = {
    "r2": metrics.get_scorer("r2"),
    "rmse": metrics.get_scorer("neg_mean_squared_error"),
    "mae": metrics.get_scorer("neg_mean_absolute_error"),
    "poisson_dev": metrics.make_scorer(
        lambda y_true, y_pred: -1
        * metrics.mean_poisson_deviance(y_true, np.clip(y_pred, 0.1, None))
    ),
    "rmse_weighted": metrics.make_scorer(
        lambda y_true, y_pred: -1
        * metrics.mean_squared_error(
            y_true,
            y_pred,
            sample_weight=np.square(np.argsort(np.argsort(y_pred)) / len(y_pred)),
        )
    ),
    "rmse_top_5": metrics.make_scorer(
        lambda y_true, y_pred: -1
        * metrics.mean_squared_error(
            y_true,
            y_pred,
            sample_weight=np.where(y_pred >= np.quantile(y_pred, 0.95), 1, 0),
        )
    ),
}
SCORING_MAIN = "poisson_dev"

# Creds
DATABRICKS_USERNAME = os.environ["DATABRICKS_USERNAME"]
SERVER = os.environ["SERVER"] + ".database.windows.net"
DATABASE = os.environ["DATABASE"]
USERNAME = os.environ["USERNAME"]
PASSWORD = "{" + os.environ["PASSWORD"] + "}"
DRIVER = "{ODBC Driver 17 for SQL Server}"
CONN_STR = (
    "mssql+pyodbc:///?odbc_connect="
    f"DRIVER={DRIVER}"
    f";SERVER=tcp:{SERVER}"
    f";PORT=1433;DATABASE={DATABASE}"
    f";UID={USERNAME}"
    f";PWD={PASSWORD}"
)
DRAFT_URL = os.environ["DRAFT_URL"]
DRAFT_KEY = os.environ["DRAFT_KEY"]

# Directories.
THIS_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(THIS_DIR)
QUERY_PATH = os.path.join(THIS_DIR, "query.sql")
MODEL_PATH = os.path.join(THIS_DIR, "model.joblib")
FEATURES_PATH = os.path.join(THIS_DIR, "features.json")

# Features and target.
HOLDOUT_SEASON = 2021
TARGET = "points_clipped"
FEATURES = [
    "position",
    "round",
    "mean_prev",
    "price_prev",
    "variation_prev",
    "matches_prev",
    "spi",
    "spi_opp",
    "prob_win",
    "prob_lose",
    "prob_tie",
    "proj_score",
    "proj_score_opp",
    "importance",
    "importance_opp",
]

# Simulation
SCHEME = {
    "goalkeeper": 1,
    "fullback": 2,
    "defender": 2,
    "midfielder": 3,
    "forward": 3,
    "coach": 1,
}
SCHEME_EXPRESS = {
    "goalkeeper": 1,
    "fullback": 2,
    "defender": 2,
    "midfielder": 3,
    "forward": 3,
    "coach": 0,
}
ALGO = "genetic"
MAX_PLAYERS_PER_CLUB = 5

warnings.filterwarnings("ignore")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

logging.info("Define estimators")
ESTIMATOR = make_pipeline(
    make_column_transformer(
        (OneHotEncoder(sparse=False), (0,)),
        remainder=PowerTransformer(),
    ),
    HistGradientBoostingRegressor(random_state=RANDOM_STATE),
)

ESTIMATOR.set_params(
    **{
        "histgradientboostingregressor__l2_regularization": 0.27506819465722815,
        "histgradientboostingregressor__learning_rate": 0.018676715976865585,
        "histgradientboostingregressor__loss": "poisson",
        "histgradientboostingregressor__max_bins": 207,
        "histgradientboostingregressor__max_depth": 16,
        "histgradientboostingregressor__max_iter": 258,
        "histgradientboostingregressor__max_leaf_nodes": 76,
        "histgradientboostingregressor__min_samples_leaf": 63,
    }
)


@dataclass
class Objective:
    """Optuna objective."""

    X: pd.DataFrame
    y: pd.Series
    scoring: Callable
    cv: int

    def __call__(self, trial):
        # params = {
        #     "histgradientboostingregressor__loss": trial.suggest_categorical(
        #         "histgradientboostingregressor__loss",
        #         ["poisson"],  # , "squared_error", "absolute_error"],
        #     ),
        #     "histgradientboostingregressor__learning_rate": trial.suggest_float(
        #         "histgradientboostingregressor__learning_rate", 0.001, 1, log=True
        #     ),
        #     "histgradientboostingregressor__max_iter": trial.suggest_int(
        #         "histgradientboostingregressor__max_iter", 10, 1000, log=True
        #     ),
        #     "histgradientboostingregressor__max_leaf_nodes": trial.suggest_int(
        #         "histgradientboostingregressor__max_leaf_nodes", 16, 2048
        #     ),
        #     "histgradientboostingregressor__max_depth": trial.suggest_int(
        #         "histgradientboostingregressor__max_depth", 2, 128
        #     ),
        #     "histgradientboostingregressor__min_samples_leaf": trial.suggest_int(
        #         "histgradientboostingregressor__min_samples_leaf", 2, 512
        #     ),
        #     "histgradientboostingregressor__l2_regularization": trial.suggest_float(
        #         "histgradientboostingregressor__l2_regularization", 0.001, 10, log=True
        #     ),
        #     "histgradientboostingregressor__max_bins": trial.suggest_int(
        #         "histgradientboostingregressor__max_bins", 2, 255
        #     ),
        # }
        # ESTIMATOR.set_params(**params)
        return cross_val_score(
            ESTIMATOR,
            self.X,
            self.y,
            scoring=self.scoring,
            cv=self.cv,
        ).mean()


def simulate(
    data,
    scheme,
    budget,
    algorithm,
    max_players_per_club,
    express,
):
    """Simulate a Cartola FC season."""
    col_map = {
        "player": "id",
        "position": "position",
        "price_prev": "price",
        "points_pred": "points",
        "points": "actual_points",
        "variation": "actual_variation",
        "club": "club",
    }

    if data["season"].nunique() > 1:
        raise ValueError("You cannot simulate more than a single season.")

    history = []
    for i, rnd in data.sort_values("round").groupby("round", as_index=False):
        logging.info("Simulate round %s", i)
        rnd = rnd[col_map.keys()].rename(col_map, axis=1)

        players = rnd[["id", "club", "position", "price", "points"]]
        body = {
            "scheme": scheme,
            "algorithm": algorithm,
            "price": budget,
            "players": players.to_dict("records"),
            "max_players_per_club": max_players_per_club,
        }
        res = requests.post(
            DRAFT_URL,
            params={"code": DRAFT_KEY},
            data=json.dumps(body),
            verify=False,
        )
        if res.status_code >= 300:
            raise ValueError(res.text)

        line_up = pd.DataFrame.from_records(json.loads(res.content.decode())["players"])
        line_up = line_up.merge(
            rnd[["id", "actual_points", "actual_variation"]],
            how="left",
            on="id",
        )

        if not express:
            captain_idx = line_up["points"].nlargest(1).index[0]
            line_up.at[captain_idx, "points"] *= 2
            line_up.at[captain_idx, "actual_points"] *= 2

        price = line_up["price"].sum()
        actual_variation = line_up["actual_variation"].sum()
        actual_points = line_up["actual_points"].sum()
        expected_points = line_up["points"].sum()

        history.append(
            {
                "Round": rnd,
                "Budget": budget,
                "Price": price,
                "Expected Points": expected_points,
                "Actual Points": actual_points,
                "Actual Variation": actual_variation,
            }
        )
        if not express:
            budget += actual_variation

    return pd.DataFrame.from_records(history)


def main():
    """Main execution."""
    mlflow.set_tracking_uri("databricks")
    mlflow.set_experiment(f"/Users/{DATABRICKS_USERNAME}/cartola-forecast")
    with mlflow.start_run():
        mlflow.log_artifact(__file__)

        logging.info("Creat SQLAlchemy engine")
        engine = create_engine(CONN_STR)
        logging.info("Load query")
        with open(QUERY_PATH, encoding="utf-8") as file:
            query = file.read()
        mlflow.log_text(query, "data/query.sql")
        logging.info("Query the database")
        data = pd.read_sql(sql=query, con=engine)

        logging.info("Split datasets")
        train = data[data["season"] < HOLDOUT_SEASON]
        test = data[data["season"] == HOLDOUT_SEASON]
        X_train = train[FEATURES]
        X_test = test[FEATURES]
        y_train = train[TARGET]
        y_test = test[TARGET]
        for key, val in {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }.items():
            mlflow.log_text(val.to_csv(index=False), f"data/{key}.csv")

        mlflow.log_text(str(ESTIMATOR), "model_repr.txt")
        mlflow.log_param("scoring", SCORING_MAIN)

        logging.info("Optimize hyperparams with Optuna")
        study = optuna.create_study(direction="maximize")
        study.optimize(
            Objective(X=X_train, y=y_train, scoring=SCORINGS[SCORING_MAIN], cv=5),
            n_trials=N_TRIALS,
            timeout=TIMEOUT,
        )
        logging.info("Best params are: %s", study.best_params)
        mlflow.log_param("n_trials", len(study.trials))
        mlflow.log_params(study.best_params)

        logging.info("Evaluate model on test dataset")
        ESTIMATOR.set_params(**study.best_params)
        ESTIMATOR.fit(X_train, y_train)

        logging.info("Score model")
        for scoring, scorer in SCORINGS.items():
            score = scorer(ESTIMATOR, X_test, y_test)
            logging.info("%s: %s", scoring, score)
            mlflow.log_metric(scoring, score)

        test["points_pred"] = ESTIMATOR.predict(X_test)
        logging.info("Simulate a season of standard Cartola FC")
        sim_std = simulate(
            data=test,
            scheme=SCHEME,
            budget=100,
            algorithm=ALGO,
            max_players_per_club=MAX_PLAYERS_PER_CLUB,
            express=False,
        )
        mlflow.log_metric("simulation_standard", sim_std["Actual Points"].sum())
        logging.info("Cumulative points %s", sim_std["Actual Points"].sum())
        logging.info("Simulate a season of Cartola FC express")
        sim_exp = simulate(
            data=test,
            scheme=SCHEME_EXPRESS,
            budget=100,
            algorithm=ALGO,
            max_players_per_club=MAX_PLAYERS_PER_CLUB,
            express=True,
        )
        mlflow.log_metric("simulation_expresss", sim_exp["Actual Points"].sum())
        logging.info("Cumulative points %s", sim_exp["Actual Points"].sum())

        logging.info("Calculate importances.")
        importances = pd.Series(
            permutation_importance(
                ESTIMATOR,
                X_test,
                y_test,
                scoring=SCORINGS[SCORING_MAIN],
                random_state=RANDOM_STATE,
            )["importances_mean"],
            index=FEATURES,
        ).sort_values(ascending=False)
        mlflow.log_text(importances.to_json(), "importances.json")

        fig, ax = plt.subplots()
        importances.sort_values(ascending=True).plot.barh(color="darkorange", ax=ax)
        fig.tight_layout()
        mlflow.log_figure(fig, "importances.png")

        logging.info("Retrain on whole dataset")
        ESTIMATOR.fit(pd.concat((X_train, X_test)), pd.concat((y_train, y_test)))

        logging.info("Export feature list")
        with open(FEATURES_PATH, mode="w", encoding="utf-8") as file:
            json.dump(FEATURES, file, sort_keys=False, indent=4)
        mlflow.log_artifact(FEATURES_PATH)

        logging.info("Export model")
        joblib.dump(ESTIMATOR, MODEL_PATH)
        mlflow.log_artifact(MODEL_PATH)


if __name__ == "__main__":
    main()
