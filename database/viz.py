"""Notebook for data visualization."""
# %%

import os

import pandas as pd

import utils.cockroachdb

THIS_DIR = os.path.dirname(__file__)

# %%

engine = utils.cockroachdb.create_engine(
    user=os.environ["USER"],
    password=os.environ["PASSWORD"],
    host=os.environ["HOST"],
    port=os.environ["PORT"],
    database=os.environ["DATABASE"],
    options=os.environ["OPTIONS"],
)

# %%

with open(os.path.join(THIS_DIR, "query.sql")) as file:
    query = file.read()

df = pd.read_sql("SELECT * FROM fivethirtyeight.spi", con=engine, index_col=None)
df.sample(5)
