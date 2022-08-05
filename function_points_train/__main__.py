"""CLI for training points model."""

import argparse
import json
import logging
import os
import sys
from decimal import Decimal

import pandas as pd
import requests
import sktune
import wandb
from sklearn.metrics import get_scorer

from .main import get_data

THIS_DIR = os.path.dirname(__file__)

# Default Args
ESTIMATOR = os.path.join(THIS_DIR, "xp-in.yml")
QUERY_TRAIN = os.path.join(THIS_DIR, "query_train.sql")
QUERY_TEST = os.path.join(THIS_DIR, "query_test.sql")
QUERY_DRAFT = os.path.join(THIS_DIR, "query_draft.sql")
TARGET = "total_points"
INDEX = "id"
METRIC = "neg_mean_poisson_deviance"
DIRECTION = "maximize"
N_TRIALS = 1
TIMEOUT = None
OUTPUT = os.path.join(THIS_DIR, "xp-out.yml")

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname).1s %(asctime)s] %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)

# WandB
os.environ["WANDB_SILENT"] = "true"

# Draft API
DRAFT_URL = os.environ["DRAFT_URL"]
DRAFT_KEY = os.environ["DRAFT_KEY"]


def get_draft_data(path, players_ids):
    """Get draft data."""
    with open(path, encoding="utf-8") as file:
        query = file.read()
    query = query.format(players_ids=",".join(map(str, players_ids)))
    return pd.read_gbq(query, index_col="id")


class DecimalEncoder(json.JSONEncoder):
    """Decimal encoder for JSON."""

    def default(self, obj):
        """Encode Decimal."""
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


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
        "output": {"Payload": data.to_dict(orient="records")},
    }
    res = requests.post(
        DRAFT_URL,
        params={"Content-Type": "application/json", "x-api-key": DRAFT_KEY},
        data=json.dumps(body, cls=DecimalEncoder),
    )
    if res.status_code >= 300:
        raise ValueError(res.text)
    return sum(p["actual_points"] for p in json.loads(res.content.decode())["players"])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--estimator", default=ESTIMATOR)
    parser.add_argument("--query-train", default=QUERY_TRAIN)
    parser.add_argument("--query-test", default=QUERY_TEST)
    parser.add_argument("--target", default=TARGET)
    parser.add_argument("--index", default=INDEX)
    parser.add_argument("--metric", default=METRIC)
    parser.add_argument("--direction", default=DIRECTION)
    parser.add_argument("--n-trials", default=N_TRIALS, type=int)
    parser.add_argument("--timeout", default=TIMEOUT, type=int)
    parser.add_argument("--output", default=OUTPUT)
    parser.add_argument("-m", "--message", default="")
    args = parser.parse_args()

    wandb.init(project="palpiteiro-points", save_code=True, notes=args.message)
    wandb.log(
        {
            "target": args.target,
            "index": args.index,
            "metric": args.metric,
            "direction": args.direction,
            "n-trials": args.n_trials,
            "timeout": args.timeout,
        }
    )

    wandb.save(args.query_train)
    wandb.save(args.query_test)
    logging.info("Get training data")
    x_train, y_train = get_data(args.query_train, args.target, args.index)
    logging.info("Get testing data")
    x_test, y_test = get_data(args.query_test, args.target, args.index)

    wandb.save(args.estimator)
    logging.info("Start tuning")
    estimator = sktune.tune(
        path=args.estimator,
        x=x_train,
        y=y_train,
        scoring=args.metric,
        cv=5,
        n_trials=args.n_trials,
        timeout=args.timeout,
        direction=args.direction,
        output=args.output,
    )

    estimator.fit(x_train, y_train)
    wandb.save(args.output)

    score = get_scorer(args.metric)(estimator, x_test, y_test)
    logging.info("Score %s", score)
    wandb.log({"score": score})

    logging.info("Get draft data")

    draft_data = get_draft_data(QUERY_DRAFT, x_test.index).convert_dtypes()
    y_pred = pd.Series(
        estimator.predict(x_test), index=x_test.index, name="expected_points"
    )
    draft_data = draft_data.join(y_pred)
    points = draft(draft_data, max_players_per_club=5, dropout=0.1)
    logging.info("Points %s", points)

    logging.info("Run URL: %s", wandb.run.get_url())
