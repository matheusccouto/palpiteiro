"""CLI for training points model."""

import argparse
import json
import logging
import os
import sys
from decimal import Decimal

import numpy as np
import pandas as pd
import requests
import sktune
import wandb
from sklearn.inspection import permutation_importance
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
MAX_PLAYERS_PER_CLUB = 5
DROPOUT = 0.333
TIMES = 10
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

# Pandas
pd.set_option("mode.chained_assignment", None)

# Draft API
DRAFT_URL = os.environ["DRAFT_URL"]
DRAFT_KEY = os.environ["DRAFT_KEY"]


def get_draft_data(path, players_ids):
    """Get draft data."""
    with open(path, encoding="utf-8") as file:
        query = file.read()
    query = query.format(players_ids=",".join(map(str, players_ids)))
    return pd.read_gbq(query, index_col="play_id")


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
        "output": {"Payload": data.to_dict(orient="records")},
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


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--estimator", default=ESTIMATOR)
    parser.add_argument("--query-train", default=QUERY_TRAIN)
    parser.add_argument("--query-test", default=QUERY_TEST)
    parser.add_argument("--target", default=TARGET)
    parser.add_argument("--index", default=INDEX)
    parser.add_argument("--max-players-per-club", default=MAX_PLAYERS_PER_CLUB)
    parser.add_argument("--dropout", default=DROPOUT)
    parser.add_argument("--times", default=TIMES)
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


    # Tuning

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
    wandb.log({args.metric: score})


    # Feature importances

    logging.info("Calculate feature importances.")
    importances = pd.Series(
        permutation_importance(
            estimator,
            x_test,
            y_test,
            scoring=args.metric,
        )["importances_mean"],
        index=x_test.columns,
    ).sort_values(ascending=False)
    table = wandb.Table(
        data=list(importances.iteritems()),
        columns=["feature", "importance"],
    )
    importance_plot = wandb.plot.bar(
        table,
        label="feature",
        value="importance",
        title="Permutation Importance",
    )


    # Draft simulation

    logging.info("Get draft data")

    draft_data = get_draft_data(QUERY_DRAFT, x_test.index).convert_dtypes()
    y_pred = pd.Series(
        estimator.predict(x_test),
        index=x_test.index,
        name="points",
    )
    draft_data = draft_data.join(y_pred)

    sim = {}
    ref = {}
    for all_time_round in sorted(draft_data["all_time_round"].unique()):
        rnd_data = draft_data[draft_data["all_time_round"] == all_time_round]
        sim[all_time_round] = [
            draft(
                rnd_data,
                max_players_per_club=args.max_players_per_club,
                dropout=args.dropout,
            )
            for _ in range(args.times)
        ]
        rnd_data["points"] = rnd_data["actual_points"]
        ref[all_time_round] = draft(
            rnd_data,
            max_players_per_club=args.max_players_per_club,
            dropout=args.dropout,
        )
        logging.info(
            "Round %03d - Avg: %.1f Std: %.1f Max: %.1f Min: %.1f Ref: %.1f",
            all_time_round,
            np.mean(sim[all_time_round]),
            np.std(sim[all_time_round]),
            max(sim[all_time_round]),
            min(sim[all_time_round]),
            ref[all_time_round],
        )


    # Scoring

    normalized_score_mean = [np.mean(v) / ref[k] for k, v in sim.items()]
    normalized_score_std = [np.std(v) / ref[k] for k, v in sim.items()]
    wandb.log(
        {
            "mean_normalized_score_mean": np.mean(normalized_score_mean),
            "std_normalized_score_mean": np.std(normalized_score_mean),
            "mean_normalized_score_std": np.mean(normalized_score_std),
            "std_normalized_mean_std": np.std(normalized_score_std),
        }
    )


    # Time series scoring

    table = wandb.Table(
        data=[
            [rnd, normalized_score_mean[i], normalized_score_std[i]]
            for i, rnd in enumerate(sim)
        ],
        columns=["round", "normalized score mean", "normalized score std"],
    )
    plot = wandb.plot.line(
        table,
        x="round",
        y="normalized score mean",
        title="Normalized Score Mean",
    )
    wandb.log({"normalized_score_mean_plot": plot})


    logging.info("Run URL: %s", wandb.run.get_url())
