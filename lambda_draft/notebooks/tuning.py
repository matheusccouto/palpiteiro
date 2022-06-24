# %% [markdown]
# # Genetic Algorithm Tuning

# %% [markdown]
# ## Setup
# Change directory to the root folder to be able to import modules.

# %%
import os

THIS_FOLDER = os.path.dirname(os.path.realpath("__file__"))
ROOT_FOLDER = os.path.dirname(THIS_FOLDER)
os.chdir(ROOT_FOLDER)

# %% [markdown]
# Setup logging.

# %%
import logging
import sys

logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

# %% [markdown]
# Contants to be used throughout the notebook.

# %%
from draft import Scheme

BUDGET = 140
MAX_PLAYERS_PER_CLUB = 5
SCHEME = Scheme(
    goalkeeper=1,
    defender=2,
    fullback=2,
    midfielder=3,
    forward=3,
    coach=0,
)

# %% [markdown]
# ## Load Players Data

# %%
from tests.helper import load_players

players = load_players()
print(f"There are {len(players)} players in this set.")

# %% [markdown]
# ## Estimate Max Points

# %% [markdown]
# Create combinations

# %%
import itertools

import num2words

from draft.algorithm import players_per_position

by_pos = players_per_position(players)

positions_combos = {}
length = 1
for key, val in by_pos.items():
    positions_combos[key] = list(itertools.combinations(by_pos[key], r=SCHEME[key]))
    print(f"{key.capitalize()}: {len(positions_combos[key])}")
    length *= len(positions_combos[key])

print(f"\nThere are {num2words.num2words(length)} combinations")

# %% [markdown]
# There are so many possible combinations that it is not possible to evaluate it all.
# I will use a sample to estimate the most probable maximum.

# %%
import random

from draft import LineUp

N_TIMES = 10000


def get_random_line_up(combos, budget, scheme, max_players_per_club):
    """Get a random line up."""
    while True:

        players_nested = [random.choice(val) for val in combos.values()]
        players_flatten = [p for pos in players_nested for p in pos]
        line_up = LineUp(scheme=scheme, players=players_flatten, bench=[])

        if line_up.price > budget:
            continue

        if max(line_up.players_per_club.values()) > max_players_per_club:
            continue

        yield line_up


points_sample = [
    next(
        get_random_line_up(
            positions_combos,
            BUDGET,
            SCHEME,
            MAX_PLAYERS_PER_CLUB,
        )
    ).points
    for _ in range(N_TIMES)
]

# %% [markdown]
# Fit the sample to some  distributions and evaluate goodness of fit.

# %%
import numpy as np
import plotly.graph_objects as go
from scipy import stats

fig = go.Figure()
fig.add_trace(
    go.Histogram(x=points_sample, histnorm="probability density", name="sample")
)

max_p = 0
dist_best = None
for dist in (stats.lognorm, stats.chi2, stats.gamma):

    args = dist.fit(points_sample)
    x = np.linspace(min(points_sample), max(points_sample))
    y = dist.pdf(x, *args)
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=dist.name))

    _, p = stats.kstest(points_sample, dist.cdf, args=args)
    if p > max_p:
        dist_best = dist
        args_best = args
        max_p = p

print(f"The selected dist is {dist_best.name} with a p-value of {max_p}")

fig.show()

# %% [markdown]
# ## Estimate

# %%
max_points = dist_best.ppf(1 - (N_TIMES / length), *args_best)
print(f"{max_points = }")

# %% [markdown]
# ### Metric
# Tuning needs a metric that reflects the goal.
# The goal is to have the algorithm running enough time to find the best result, but not longer than the minimum necessary.
# 
# The 3D plot confirms that the metric is higher (darker) where points are higher, variance is lower and time elapsed is lower.

# %%
import itertools

import numpy as np
import pandas as pd
import plotly.express as px

MAX_POINTS = max_points  # team points
MAX_DIFF = 0.1  # Difference ratio
MAX_TIME = 3  # Seconds


def metric(points, diff, time_elapsed):
    """Optimization metric."""
    return np.product(
        (
            np.sinh(points / MAX_POINTS),
            np.tanh(MAX_DIFF / diff),
            np.tanh(MAX_TIME / time_elapsed),
        ),
        axis=0,
    )


points_arr = np.linspace(start=MAX_POINTS, stop=0, num=9, endpoint=False)
diff_arr = np.linspace(start=MAX_DIFF, stop=0, num=9, endpoint=False)
time_arr = np.linspace(start=MAX_TIME, stop=0, num=9, endpoint=False)

# Cross product and transpose.
data = zip(*itertools.product(points_arr, diff_arr, time_arr))
df = pd.DataFrame(data, index=["Points", "Difference", "Time Elapsed"]).transpose()
df["Metric"] = metric(df["Points"], df["Difference"], df["Time Elapsed"])

fig = px.scatter_3d(
    df,
    x="Points",
    y="Difference",
    z="Time Elapsed",
    color="Metric",
    color_continuous_scale=px.colors.sequential.Oranges,
    template="plotly_white",
)
fig.update_traces(marker=dict(size=15, line=dict(width=0)))
fig.update_layout(
    scene=dict(
        xaxis=dict(showbackground=False),
        yaxis=dict(showbackground=False),
        zaxis=dict(showbackground=False),
    ),
)
fig.show()

# %% [markdown]
# ## Tuning

# %%
import time

import optuna
import optuna.logging

from draft.algorithm.genetic import Genetic

optuna.logging.set_verbosity(optuna.logging.ERROR)

N_TIMES = 5
N_TRIALS = 100


def factory(n_generations, n_individuals):
    """Create an alogirthm instance."""
    return Genetic(
        players=players,
        n_generations=n_generations,
        n_individuals=n_individuals,
    )


def score(algo):
    """Score algorithm."""
    start = time.time()
    line_ups = [
        algo.draft(BUDGET, SCHEME, MAX_PLAYERS_PER_CLUB) for _ in range(N_TIMES)
    ]
    end = time.time()

    # Time elapsed
    time_elapsed = (end - start) / N_TIMES

    # Mean points
    points = [line_up.points for line_up in line_ups]
    points = np.mean(points)

    # Mean price
    price = [line_up.price for line_up in line_ups]
    price = np.mean(price)

    # Line up diff
    id_sets = [set(line_up.players) for line_up in line_ups]
    diff = [
        len(left.difference(right))
        for i, left in enumerate(id_sets)
        for j, right in enumerate(id_sets)
        if i != j
    ]
    diff = np.mean(diff) / sum(SCHEME.values())

    return {
        "score": metric(points, diff, time_elapsed),
        "points": points,
        "difference": diff,
        "time_elapsed": time_elapsed,
        "price": price,
    }


def objective(trial):
    """Function to be optimized by optuna."""

    n_generations = trial.suggest_int("n_generations", 10, 500)
    n_individuals = trial.suggest_int("n_individuals", 10, 500)

    algo = factory(
        n_generations=n_generations,
        n_individuals=n_individuals,
    )
    results = score(algo)
    logging.info(
        "%.03d score=%.3f points=%.2f diff=%.2f time=%.2f price=%.2f",
        trial.number,
        results["score"],
        results["points"],
        results["difference"],
        results["time_elapsed"],
        results["price"],
    )
    return results["score"]


study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=N_TRIALS)
study.best_params

# %%
algo = factory(**study.best_params)
results = score(algo)

print(f"Points = {results['points']}")
print(f"Difference = {results['difference']}")
print(f"Time = {results['time_elapsed']}")
print(f"Price = {results['price']}")

# %% [markdown]
# ### Analyze Results

# %% [markdown]
# The next plot is used to check if there were enough trials to converge the objective value.

# %%
import optuna.visualization

fig = optuna.visualization.plot_optimization_history(study)
fig.show()

# %% [markdown]
# The importances plot helps tos understand which params really matters.

# %%
fig = optuna.visualization.plot_param_importances(study)
fig.show()

# %% [markdown]
# The parallel coordinates plot can be confused at a first glance, but it is really helpfull to quick visualize if a params works better with higher or lower values.

# %%
optuna.visualization.plot_parallel_coordinate(study)


