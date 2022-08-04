"""CLI for training points model."""

import argparse
import json
import logging
import os
import sys

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
TARGET = "total_points"
INDEX = "id"
METRIC = "neg_mean_poisson_deviance"
DIRECTION = "maximize"
N_TRIALS = 100
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


def draft(data, scheme, budget, max_players_per_club, dropout):
    """Simulate a Cartola FC season."""
    body = {
        "game": "custom",
        "scheme": scheme,
        "price": budget,
        "max_players_per_club": max_players_per_club,
        "bench": False,
        "dropout": dropout,
        "output": {"Payload": data.to_dict(orient="records")},
    }
    res = requests.post(
        DRAFT_URL,
        params={"Content-Type": "application/json", "x-api-key": DRAFT_KEY},
        data=json.dumps(body),
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

    wandb.sklearn.plot_regressor(
        estimator,
        x_train,
        x_test,
        y_train,
        y_test,
        model_name="test",
    )
    wandb.finish()

    logging.info("Run URL: %s", wandb.run.get_url())
