"""Notebook for data visualization."""
# %%

import os

import missingno as msno
import pandas as pd
import sqlalchemy

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

df = pd.read_sql("SELECT * FROM cartola.partidas", con=engine, index_col=None)
df.sample(5)

# %%

msno.matrix(df.sort_values(["temporada_id", "rodada_id", "clube_id", "atleta_id"]))
