"""Notebook for data visualization."""
# %%

import os

import pandas as pd

import utils.cockroachdb

# %%

engine = utils.cockroachdb.create_engine(
    user=os.environ["USER"],
    password=os.environ["PASSWORD"],
    host=os.environ["HOST"],
    port=os.environ["PORT"],
    database="dev",#os.environ["DATABASE"],
    options=os.environ["OPTIONS"],
)

# %%

# import pandas as pd

# SPI_URL = "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv"

# data = pd.read_csv(SPI_URL)
# data = data[data["league_id"] == 2105]
# data.to_sql("spi", engine, "fivethirtyeight", index=False, method="multi")  #, if_exists="replace")


# %%

# utils.cockroachdb.run('CREATE SCHEMA fivethirtyeight', engine)
