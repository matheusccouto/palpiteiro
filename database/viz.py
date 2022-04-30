"""Notebook for data visualization."""
# %%

import os

import missingno as msno
import pandas as pd
import sqlalchemy

import utils.cockroachdb

# %%

conn_str = utils.cockroachdb.create_connection_string(
    user=os.environ["USER"],
    password=os.environ["PASSWORD"],
    host=os.environ["HOST"],
    port=os.environ["PORT"],
    database=os.environ["DATABASE"],
    options=os.environ["OPTIONS"],
)
engine = sqlalchemy.create_engine(conn_str)

df = pd.read_sql("SELECT * FROM test.append", con=conn_str)
df.sample(5)

# %%

msno.matrix(df.sort_values(["temporada_id", "rodada_id", "clube_id", "atleta_id"]))
