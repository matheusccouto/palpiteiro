"""CLI for training points model."""

import argparse
import os

from utils.tune import tune

THIS_DIR = os.path.dirname(__file__)

PIPELINE = os.path.join(THIS_DIR, "xp.yml")
QUERY_TRAIN = os.path.join(THIS_DIR, "query_train.sql")
QUERY_TEST = os.path.join(THIS_DIR, "query_test.sql")
TARGET = "total_points"
METRIC = "neg_mean_poisson_deviance"
N_TRIALS = 100
TIMEOUT = None
OUTPUT = os.path.join(THIS_DIR, "pipeline.yml")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", default=PIPELINE)
    parser.add_argument("--query-train", default=QUERY_TRAIN)
    parser.add_argument("--query-test", default=QUERY_TEST)
    parser.add_argument("--target", default=TARGET)
    parser.add_argument("--metric", default=METRIC)
    parser.add_argument("--n-trials", default=N_TRIALS, type=int)
    parser.add_argument("--timeout", default=TIMEOUT, type=int)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    tune(
        pipeline=args.pipeline,
        query_train=args.query_train,
        query_test=args.query_test,
        target=args.target,
        metric=args.metric,
        n_trials=args.n_trials,
        timeout=args.timeout,
        output=args.output,
    )
