"""Notebook for data exploration."""
# %%

import os

import utils.cockroachdb

# %%

engine = utils.cockroachdb.create_engine(
    user=os.environ["USER"],
    password=os.environ["PASSWORD"],
    host=os.environ["HOST"],
    port=os.environ["PORT"],
    database=os.environ["DATABASE"],
    options=os.environ["OPTIONS"],
)

utils.cockroachdb.run("SELECT * FROM cartola.atletas", engine)
