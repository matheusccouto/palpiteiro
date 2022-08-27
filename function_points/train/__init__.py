"""Train model."""

# pylint: disable=wrong-import-position

# %% [markdown]
# ## Load data from warehouse

# %%
import logging
import os
import sys

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname).1s %(asctime)s] %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)

THIS_DIR = os.path.dirname(__file__)
QUERY_TRAIN = os.path.join(THIS_DIR, "train.sql")
ID_COL = "id"

with open(QUERY_TRAIN, encoding="utf-8") as file:
    df = pd.read_gbq(file.read(), index_col=ID_COL)

df.head()

# %% [markdown]
# ## Split data based on time

# %%
TARGET_COL = "total_points"
TIME_COL = "all_time_round"
CLUB_COL = "club"
PRICE_COL = "price"
POSITION_COL = "position"

test_itv = (df[TIME_COL].max() - 38, df[TIME_COL].max())
valid_itv = (test_itv[0] - 38, test_itv[0] - 1)
train_itv = (df[TIME_COL].min(), valid_itv[0] - 1)

df = df.sort_values(TIME_COL)
train = df[(df[TIME_COL] >= train_itv[0]) & (df[TIME_COL] <= train_itv[1])]
valid = df[(df[TIME_COL] >= valid_itv[0]) & (df[TIME_COL] <= valid_itv[1])]
test = df[(df[TIME_COL] >= test_itv[0]) & (df[TIME_COL] <= test_itv[1])]

to_drop = [TARGET_COL, TIME_COL, CLUB_COL, PRICE_COL, POSITION_COL]

x_train = train.drop(columns=to_drop)
y_train = train[TARGET_COL]
q_train = train["all_time_round"].value_counts().sort_index()

x_valid = valid.drop(columns=to_drop)
y_valid = valid[TARGET_COL]
q_valid = valid["all_time_round"].value_counts().sort_index()

x_test = test.drop(columns=to_drop)
y_test = test[TARGET_COL]
q_test = test["all_time_round"].value_counts().sort_index()

print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)


# %% [markdown]
# ## Train machine learning model

# %%

from copy import deepcopy

import lightgbm as lgbm
import numpy as np
import optuna
from sklearn.metrics import ndcg_score

ESTIMATOR = lgbm.LGBMRanker(n_estimators=100, n_jobs=-1)
N_TRIALS = 1
TIMEOUT = None
NDCG_P = 0.1


def fit_predict(estimator, x_train, y_train, q_train, x_test, q_test):
    """Fit and predict estimator."""
    estimator.fit(
        X=x_train.astype("float64"),
        y=y_train.round().clip(0, 30).astype("int"),
        group=q_train.astype("int").tolist(),
    )
    return pd.Series(
        estimator.predict(
            X=x_test.astype("float64"),
            group=q_test.astype("int").tolist(),
        ),
        index=x_test.index,
        name=y_train.name
    )


def ndcg(y_true, y_pred, groups, p=1.0):
    """Mean groups NDCG"""
    i = 0
    scores = []
    for g in groups.cumsum():
        scores.append(
            ndcg_score(
                y_true[i:g].values.reshape(1, -1),
                y_pred[i:g].values.reshape(1, -1),
                k=round(p * len(y_pred[i:g])),
            )
        )
        i = g
    return np.mean(scores)


class Objective:
    """Optuna objective."""

    def __init__(self, estimator, x_train, y_train, q_train, x_test, y_test, q_test):
        self.estimator = estimator
        self.x_train = x_train
        self.y_train = y_train
        self.q_train = q_train
        self.x_test = x_test
        self.y_test = y_test
        self.q_test = q_test

    def __call__(self, trial: optuna.Trial):
        params = dict(
            boosting_type=trial.suggest_categorical(
                "boosting_type", ["gbdt", "dart", "goss"]
            ),
            num_leaves=trial.suggest_int("num_leaves", 2, 1024),
            max_depth=trial.suggest_int("max_depth", 2, 128),
            learning_rate=trial.suggest_float("learning_rate", 1e-3, 1e0, log=True),
            # subsample_for_bin=trial.suggest_int("subsample_for_bin", 1000, 200000),
            # min_split_gain=trial.suggest_float("min_split_gain", 0.0, 1.0),
            min_child_weight=trial.suggest_int("min_child_weight", 1, 5),
            min_child_samples=trial.suggest_int("min_child_samples", 1, 16),
            subsample=trial.suggest_float("subsample", 0.5, 1.0),
            # subsample_freq=trial.suggest_float("subsample_freq", 0.0, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
            reg_alpha=trial.suggest_float("reg_alpha", 1e-3, 1e0, log=True),
            reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 1e0, log=True),
        )
        self.estimator.set_params(**params)
        y_pred = fit_predict(
            self.estimator,
            self.x_train,
            self.y_train,
            self.q_train,
            self.x_test,
            self.q_test,
        )
        return ndcg(self.y_test, y_pred, self.q_test, p=NDCG_P)


estimators = {}
y_preds = {}
scores = {}
for pos in df[POSITION_COL].unique():

    train_pos = train[train[POSITION_COL] == pos]
    x_train_pos = x_train.loc[train_pos.index]
    y_train_pos = y_train.loc[train_pos.index]
    q_train_pos = train_pos[TIME_COL].value_counts().sort_index()

    valid_pos = valid[valid[POSITION_COL] == pos]
    x_valid_pos = x_valid.loc[valid_pos.index]
    y_valid_pos = y_valid.loc[valid_pos.index]
    q_valid_pos = valid_pos[TIME_COL].value_counts().sort_index()

    test_pos = test[test[POSITION_COL] == pos]
    x_test_pos = x_test.loc[test_pos.index]
    y_test_pos = y_test.loc[test_pos.index]
    q_test_pos = test_pos[TIME_COL].value_counts().sort_index()

    estimators[pos] = deepcopy(ESTIMATOR)
    objective = Objective(
        estimator=estimators[pos],
        x_train=x_train_pos,
        y_train=y_train_pos,
        q_train=q_train_pos,
        x_test=x_valid_pos,
        y_test=y_valid_pos,
        q_test=q_valid_pos,
    )

    study = optuna.create_study(direction="maximize", study_name=pos)
    study.optimize(objective, n_trials=N_TRIALS, timeout=TIMEOUT)

    y_preds[pos] = fit_predict(
        estimator=estimators[pos],
        x_train=pd.concat((x_train_pos, x_valid_pos)),
        y_train=pd.concat((y_train_pos, y_valid_pos)),
        q_train=pd.concat((q_train_pos, q_valid_pos)),
        x_test=x_test_pos,
        q_test=q_test_pos,
    )

    ## Scorings

    # NDGC
    scores[pos] = ndcg(y_test_pos, y_preds[pos], q_test_pos, p=NDCG_P)
    logging.info("%s NDCG: %s", pos.capitalize(), scores[pos])


# %%

import concurrent.futures
import json
from decimal import Decimal

import numpy as np
import requests

MAX_PLAYERS_PER_CLUB = 5
DROPOUT = 0.0
N_TIMES = 1

DRAFT_URL = os.environ["DRAFT_URL"]
DRAFT_KEY = os.environ["DRAFT_KEY"]


class DecimalEncoder(json.JSONEncoder):
    """Decimal encoder for JSON."""

    def default(self, o):
        """Encode Decimal."""
        if isinstance(o, Decimal):
            return float(o)
        return json.JSONEncoder.default(self, o)


def draft(data, max_players_per_club, dropout):
    """Simulate a Cartola FC season."""
    scheme = {
        "goalkeeper": 1,
        "fullback": 2,
        "defender": 2,
        "midfielder": 3,
        "forward": 3,
        "coach": 0,
    }
    body = {
        "game": "custom",
        "scheme": scheme,
        "price": 140,
        "max_players_per_club": max_players_per_club,
        "bench": False,
        "dropout": dropout,
        "players": data.to_dict(orient="records"),
    }
    res = requests.post(
        DRAFT_URL,
        headers={"Content-Type": "application/json", "x-api-key": DRAFT_KEY},
        data=json.dumps(body, cls=DecimalEncoder),
    )
    if res.status_code >= 300:
        raise ValueError(res.text)

    content = json.loads(res.content.decode())
    if content["status"] == "FAILED":
        raise ValueError(content["cause"])

    return sum(p["actual_points"] for p in json.loads(content["output"])["players"])


mean_points = []
max_points = []
for rnd in sorted(test[TIME_COL].unique()):

    logging.info("Round %s", rnd)

    test_rnd = test[test[TIME_COL] == rnd]
    y_pred = pd.concat(y_preds.values())
    test_rnd = test_rnd.join(y_pred, rsuffix="_predicted")

    mapping = {
        ID_COL: "id",
        CLUB_COL: "club",
        POSITION_COL: "position",
        PRICE_COL: "price",
        TARGET_COL: "actual_points",
        "total_points_predicted": "points",
    }
    data = test_rnd.reset_index().rename(mapping, axis=1)[list(mapping.values())]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for _ in range(N_TIMES):
            futures.append(executor.submit(draft, data, MAX_PLAYERS_PER_CLUB, DROPOUT))
        draft_scores = [
            fut.result() for fut in concurrent.futures.as_completed(futures)
        ]

    data["points"] = data["actual_points"]
    ref = draft(data, 5, 0.0)

    mean_draft = np.mean(draft_scores)
    mean_draft_norm = mean_draft / ref
    max_draft = np.max(draft_scores)
    max_draft_norm = max_draft / ref

    logging.info("Mean Draft: %.1f (%.2f)", mean_draft, mean_draft_norm)
    logging.info("Max Draft: %.1f (%.2f)", max_draft, max_draft_norm)
    logging.info("%s", 79 * "-")

    mean_points.append(mean_draft_norm)
    max_points.append(max_draft_norm)


overall_mean_points = np.mean(mean_points)
overall_max_points = np.mean(max_points)

logging.info("Overall Mean Draft: %.2f", overall_mean_points)
logging.info("Overall Max Draft: %.2f", overall_max_points)

# %%

import joblib

for pos, estimator in estimators.items():
    with open(os.path.join(THIS_DIR, f"{pos}.joblib"), mode="wb") as file:
        joblib.dump(estimator, file)