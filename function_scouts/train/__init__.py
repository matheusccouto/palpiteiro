"""Train model."""

# pylint: disable=wrong-import-position,wrong-import-order,redefined-outer-name,invalid-name

# %% [markdown]
# ## Set up a Weights & Biases experiment

import os

# import wandb

NOTES = ""
OPTUNA_N_TRIALS = 1
OPTUNA_TIMEOUT = None
DRAFT_MAX_PLAYERS_PER_CLUB = 5
DRAFT_DROPOUT = 0.5
DRAFT_N_TIMES = 10


# os.environ["WANDB_SILENT"] = "true"
# wandb.init(
#     project="palpiteiro-points",
#     save_code=True,
#     config={
#         "optuna.n_trials": OPTUNA_N_TRIALS,
#         "optuna.timeout": OPTUNA_TIMEOUT,
#         "draft.timeout": DRAFT_MAX_PLAYERS_PER_CLUB,
#         "draft.dropout": DRAFT_DROPOUT,
#         "draft.n_times": DRAFT_N_TIMES,
#     },
# )

# %% [markdown]
# ## Load data from warehouse

# %%
import logging
import sys

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname).1s %(asctime)s] %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)

THIS_DIR = os.path.dirname(__file__)
QUERY = os.path.join(THIS_DIR, "query.sql")
ID_COL = "id"

# wandb.save(QUERY)

with open(QUERY, encoding="utf-8") as file:
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
SCOUTS = [
    "goal",
    "assist",
    "yellow_card",
    "red_card",
    "missed_shoot",
    "on_post_shoot",
    "saved_shoot",
    "received_foul",
    "received_penalty",
    "missed_penalty",
    "outside",
    "missed_pass",
    "tackle",
    "foul",
    "penalty",
    "own_goal",
    "allowed_goal",
    "no_goal",
    "save",
    "penalty_save",
]

test_itv = (df[TIME_COL].max() - 38, df[TIME_COL].max())
valid_itv = (test_itv[0] - 38, test_itv[0] - 1)
train_itv = (df[TIME_COL].min(), valid_itv[0] - 1)

df = df.sort_values(TIME_COL)
train = df[(df[TIME_COL] >= train_itv[0]) & (df[TIME_COL] <= train_itv[1])]
valid = df[(df[TIME_COL] >= valid_itv[0]) & (df[TIME_COL] <= valid_itv[1])]
test = df[(df[TIME_COL] >= test_itv[0]) & (df[TIME_COL] <= test_itv[1])]

to_drop = SCOUTS + [TARGET_COL, TIME_COL, CLUB_COL, PRICE_COL, POSITION_COL]

x_train = train.drop(columns=to_drop)
y_train = train[SCOUTS]
q_train = train["all_time_round"].value_counts().sort_index()

x_valid = valid.drop(columns=to_drop)
y_valid = valid[SCOUTS]
q_valid = valid["all_time_round"].value_counts().sort_index()

x_test = test.drop(columns=to_drop)
y_test = test[SCOUTS]
q_test = test["all_time_round"].value_counts().sort_index()

# wandb.log(
#     {
#         "x_train": x_train,
#         "y_train": y_train.to_frame(),
#         "x_valid": x_valid,
#         "y_valid": y_valid.to_frame(),
#         "x_test": x_test,
#         "y_test": y_test.to_frame(),
#     }
# )


# %% [markdown]
# ## Train machine learning model

# %%

import json
from copy import deepcopy

import joblib
import lightgbm as lgbm
import numpy as np
import optuna
from sklearn.metrics import ndcg_score, r2_score

# ESTIMATOR = lgbm.LGBMRanker(n_estimators=100, n_jobs=-1, objective="rank_xendcg")
ESTIMATOR = lgbm.LGBMRegressor(n_estimators=10, n_jobs=-1)
# wandb.log({"estimator": str(ESTIMATOR)})


def fit(estimator, x, y, q, features=None):
    """Fit estimator."""
    if features is None:
        features = x.columns
    estimator.fit(
        X=x.astype("float64"),
        y=y.astype("float64"),
        # y=y.round().clip(0, 30).astype("int"),
        # group=q.astype("int").tolist(),
    )
    return estimator


def fit_predict(estimator, x_train, y_train, q_train, x_test, q_test, features=None):
    """Fit and predict estimator."""
    # pylint: disable=too-many-arguments
    if features is None:
        features = x_train.columns
    return pd.Series(
        fit(estimator, x_train[features], y_train, q_train).predict(
            X=x_test[features].astype("float64"),
            group=q_test.astype("int").tolist(),
        ),
        index=x_test.index,
        name=y_train.name,
    )


def score(y_true, y_pred, groups, p=1.0):
    """Mean groups NDCG"""
    return r2_score(y_true, y_pred)
    # i = 0
    # scores = []
    # for g in groups.cumsum():
    #     scores.append(
    #         ndcg_score(
    #             y_true[i:g].values.reshape(1, -1),
    #             y_pred[i:g].values.reshape(1, -1),
    #             k=round(p * len(y_pred[i:g])),
    #         )
    #     )
    #     i = g
    # return np.mean(scores)


class Objective:
    """Optuna objective."""

    # pylint: disable=too-many-arguments,too-few-public-methods

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

        feats = [
            col
            for col in self.x_train.columns
            if trial.suggest_categorical(f"use_feature_{col}", [True, False])
        ]

        self.estimator.set_params(**params)
        y_pred = fit_predict(
            self.estimator,
            self.x_train[feats],
            self.y_train,
            self.q_train,
            self.x_test[feats],
            self.q_test,
        )
        return score(self.y_test.astype(float), y_pred, self.q_test)


estimators = {p: {} for p in df[POSITION_COL].unique()}
y_preds = {p: {} for p in df[POSITION_COL].unique()}
params = {p: {} for p in df[POSITION_COL].unique()}
features = {p: {} for p in df[POSITION_COL].unique()}
scores_valid = {p: {} for p in df[POSITION_COL].unique()}
scores_test = {p: {} for p in df[POSITION_COL].unique()}
for pos in df[POSITION_COL].unique():

    for scout in SCOUTS:

        train_pos = train[train[POSITION_COL] == pos]
        x_train_pos = x_train.loc[train_pos.index]
        y_train_pos = y_train.loc[train_pos.index][scout]
        q_train_pos = train_pos[TIME_COL].value_counts().sort_index()

        valid_pos = valid[valid[POSITION_COL] == pos]
        x_valid_pos = x_valid.loc[valid_pos.index]
        y_valid_pos = y_valid.loc[valid_pos.index][scout]
        q_valid_pos = valid_pos[TIME_COL].value_counts().sort_index()

        test_pos = test[test[POSITION_COL] == pos]
        x_test_pos = x_test.loc[test_pos.index]
        y_test_pos = y_test.loc[test_pos.index][scout]
        q_test_pos = test_pos[TIME_COL].value_counts().sort_index()

        estimators[pos] = {scout: deepcopy(ESTIMATOR)}
        objective = Objective(
            estimator=estimators[pos][scout],
            x_train=x_train_pos,
            y_train=y_train_pos,
            q_train=q_train_pos,
            x_test=x_valid_pos,
            y_test=y_valid_pos,
            q_test=q_valid_pos,
        )

        study = optuna.create_study(direction="maximize", study_name=f"{pos}_{scout}")
        study.optimize(objective, n_trials=OPTUNA_N_TRIALS, timeout=OPTUNA_TIMEOUT)

        scores_valid[pos][scout] = study.best_value
        params[pos][scout] = {
            key: val
            for key, val in study.best_params.items()
            if not key.startswith("use_feature_")
        }
        features[pos][scout] = [
            key.removeprefix("use_feature_")
            for key, val in study.best_params.items()
            if key.startswith("use_feature_") and val is True
        ]

        estimators[pos][scout].set_params(**params[pos][scout])
        estimators[pos][scout].set_params(n_estimators=100)  # FIXME
        y_preds[pos][scout] = fit_predict(
            estimator=estimators[pos][scout],
            x_train=pd.concat((x_train_pos, x_valid_pos))[features[pos][scout]],
            y_train=pd.concat((y_train_pos, y_valid_pos)),
            q_train=pd.concat((q_train_pos, q_valid_pos)),
            x_test=x_test_pos[features[pos][scout]],
            q_test=q_test_pos,
        )

        ## Scorings

        scores_test[pos][scout] = score(
            y_test_pos.astype(float), y_preds[pos][scout], q_test_pos
        )
        logging.info("%s Score: %s", pos.capitalize(), scores_test[pos][scout])

        # Artifacts to be uploaded later,
        est = fit(
            estimator=deepcopy(estimators[pos][scout]),
            x=pd.concat((x_train_pos, x_valid_pos, x_test_pos))[features[pos][scout]],
            y=pd.concat((y_train_pos, y_valid_pos, y_test_pos)),
            q=pd.concat((q_train_pos, q_valid_pos, q_test_pos)),
        )
        with open(os.path.join(THIS_DIR, f"{pos}_{scout}.joblib"), mode="wb") as file:
            joblib.dump(est, file)

        with open(
            os.path.join(THIS_DIR, f"{pos}_{scout}_features.json"),
            encoding="utf-8",
            mode="w",
        ) as file:
            json.dump(features[pos][scout], file)

        with open(
            os.path.join(THIS_DIR, f"{pos}_{scout}_params.json"),
            encoding="utf-8",
            mode="w",
        ) as file:
            json.dump(params[pos][scout], file)

# wandb.log(
#     {
#         "params": params,
#         "scores_valid": scores_valid,
#         "scores_test": scores_test,
#     }
# )

# %%


def offensive_points(row):
    """Points"""
    points = 0
    points += 8.0 * row["goal"]
    points += 5.0 * row["assist"]
    points += 3.0 * row["on_post_shoot"]
    points += 1.2 * row["saved_shoot"]
    points += 0.8 * row["missed_shoot"]
    points += 0.5 * row["received_foul"]
    points += 1.0 * row["received_penalty"]
    points -= 4.0 * row["missed_penalty"]
    points -= 0.1 * row["outside"]
    if row["position"] != "goalkeeper":
        points -= 0.1 * row["missed_pass"]
    return points


def defensive_points(row):
    """Points"""
    points = 0
    if row["position"] in ("goalkeeper", "defender", "fullback"):
        points += 5.0 * row["no_goal"]
    if row["position"] == "goalkeeper":
        points += 7.0 * row["penalty_save"]
    if row["position"] == "goalkeeper":
        points += 1.0 * row["save"]
    if row["position"] == "goalkeeper":
        points -= 1.0 * row["allowed_goal"]
    points += 1.2 * row["tackle"]
    points -= 3.0 * row["own_goal"]
    points -= 3.0 * row["red_card"]
    points -= 1.0 * row["yellow_card"]
    points -= 0.3 * row["foul"]
    points -= 1.0 * row["penalty"]
    return points


y_pred = (
    pd.concat({pos: pd.concat(pos_data, axis=1) for pos, pos_data in y_preds.items()})
    .reset_index(0)
    .rename(columns={"level_0": "position"})
)
y_pred["offensive_points"] = y_pred.apply(offensive_points, axis=1)
y_pred["defensive_points"] = y_pred.apply(defensive_points, axis=1)
y_pred["points"] = y_pred["offensive_points"] + y_pred["defensive_points"]


# %%

import concurrent.futures
import json
from decimal import Decimal

import requests

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
        timeout=30,
    )
    if res.status_code >= 300:
        raise ValueError(res.text)

    content = json.loads(res.content.decode())
    if content["status"] == "FAILED":
        raise ValueError(content["cause"])

    return sum(p["actual_points"] for p in json.loads(content["output"])["players"])


mean_points = []
max_points = []
draft_history = []
for rnd in sorted(test[TIME_COL].unique()):

    logging.info("Round %s", rnd)

    test_rnd = test[test[TIME_COL] == rnd]
    test_rnd = test_rnd.join(np.exp(y_pred["points"]), rsuffix="_predicted")

    mapping = {
        ID_COL: "id",
        CLUB_COL: "club",
        POSITION_COL: "position",
        PRICE_COL: "price",
        TARGET_COL: "actual_points",
        "total_points_predicted": "points",
    }
    data = test_rnd.reset_index().rename(mapping, axis=1)[list(mapping.values())]

    def run_draft():
        """Wrapper to handle error on draft()."""
        try:
            return draft(data, DRAFT_MAX_PLAYERS_PER_CLUB, DRAFT_DROPOUT)
        except ValueError as err:
            if "There are not enough players to form a line-up" in str(err):
                return draft(data, DRAFT_MAX_PLAYERS_PER_CLUB, DRAFT_DROPOUT)
            raise err

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for _ in range(DRAFT_N_TIMES):
            futures.append(executor.submit(run_draft))
        draft_scores = pd.Series(
            [fut.result() for fut in concurrent.futures.as_completed(futures)],
            index=[f"run{i}" for i in range(len(futures))],
            name=rnd,
        )

    data["points"] = data["actual_points"]
    ref = draft(data, 5, 0.0)

    mean_draft = np.mean(draft_scores)
    mean_draft_norm = mean_draft / ref
    max_draft = np.max(draft_scores)
    max_draft_norm = max_draft / ref

    logging.info("Mean Draft: %.1f (%.2f)", mean_draft, mean_draft_norm)
    logging.info("Max Draft: %.1f (%.2f)", max_draft, max_draft_norm)
    logging.info("%s", 40 * "-")

    draft_scores["max"] = ref
    draft_history.append(draft_scores)
    mean_points.append(mean_draft_norm)
    max_points.append(max_draft_norm)


overall_mean_points = np.mean(mean_points)
overall_max_points = np.mean(max_points)

logging.info("Overall Mean Draft: %.2f", overall_mean_points)
logging.info("Overall Max Draft: %.2f", overall_max_points)

# wandb.log(
#     {
#         "points": pd.DataFrame(draft_history),
#         "draft_mean_points_norm": overall_mean_points,
#         "draft_max_points_norm": overall_max_points,
#     }
# )
