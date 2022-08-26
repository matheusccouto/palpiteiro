"""Train model."""

# %% [markdown]
# ## Load data from warehouse

# %%
import os

import pandas as pd

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

df = df.sort_values(TIME_COL)
train = df[df[TIME_COL] < (df[TIME_COL].max() - 38)]  # Exclude last 38 rounds
test = df[df[TIME_COL] >= (df[TIME_COL].max() - 38)]  # Include last 38 rounds

to_drop = [TARGET_COL, TIME_COL, CLUB_COL, PRICE_COL, POSITION_COL]

x_train = train.drop(columns=to_drop)
y_train = train[TARGET_COL]
q_train = train["all_time_round"].value_counts().sort_index()

x_test = test.drop(columns=to_drop)
y_test = test[TARGET_COL]
q_test = test["all_time_round"].value_counts().sort_index()

print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)

# %% [markdown]
# ## Train machine learning model

# %%

import lightgbm as lgbm
from sklearn.metrics import ndcg_score

estimators = {}
for pos, train_pos in train.groupby(POSITION_COL, as_index=False):
    idx = train_pos.index
    q_train_pos = train_pos["all_time_round"].value_counts().sort_index()
    estimators[pos] = lgbm.LGBMRanker(n_estimators=100)
    estimators[pos].fit(
        x_train.loc[idx].astype("float64"),
        y_train.loc[idx].round().clip(0, 30).astype("int"),
        group=q_train_pos.astype("int"),
    )

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


for rnd in sorted(test[TIME_COL].unique()):
    print(rnd)

    test_rnd = test[test[TIME_COL] == rnd]
    x_test_rnd = x_test.loc[test_rnd.index]
    y_test_rnd = y_test.loc[test_rnd.index]

    y_pred_pos = {}
    for pos, test_rnd_pos in test_rnd.groupby(POSITION_COL, as_index=False):
        x_test_rnd_pos = x_test_rnd.loc[test_rnd_pos.index]
        y_test_rnd_pos = y_test_rnd.loc[test_rnd_pos.index]

        y_pred = estimators[pos].predict(x_test_rnd_pos.astype("float64"))
        k = round(len(y_pred) / 10)
        score = ndcg_score(
            y_test_rnd_pos.values.reshape(1, -1), y_pred.reshape(1, -1), k=k
        )
        print(pos, score)

        y_pred_pos[pos] = pd.Series(y_pred, index=test_rnd_pos.index, name="points")

    y_pred = pd.concat(y_pred_pos.values())
    test_rnd = test_rnd.join(y_pred)

    mapping = {
        ID_COL: "id",
        CLUB_COL: "club",
        POSITION_COL: "position",
        PRICE_COL: "price",
        TARGET_COL: "actual_points",
        "points": "points",
    }
    data = test_rnd.reset_index().rename(mapping, axis=1)[list(mapping.values())]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for _ in range(N_TIMES):
            futures.append(executor.submit(draft, data, MAX_PLAYERS_PER_CLUB, DROPOUT))
        draft_scores = [
            fut.result() for fut in concurrent.futures.as_completed(futures)
        ]

    print(np.mean(draft_scores), np.max(draft_scores))
    print()

print(np.mean(scores))
