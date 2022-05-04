"""Load players data from Cartola FC to the database."""

import io
import os

import pandas as pd

import utils.aws.s3
import utils.cockroachdb

engine = utils.cockroachdb.create_engine(
    user=os.environ["USER"],
    password=os.environ["PASSWORD"],
    host=os.environ["HOST"],
    port=os.environ["PORT"],
    database=os.environ["DATABASE"],
    options=os.environ["OPTIONS"],
)


def handler(event, context=None):
    """Lambda handler."""
    # Read existing and data to be appended.
    existing = pd.read_sql_table(event["table"], con=engine, schema=event["schema"])
    new = pd.read_csv(io.StringIO(utils.aws.s3.load(event["uri"])), index_col=0)

    # Concatenate and delete duplicated rows. Keep lasts.
    subset = event["subset"] if "subset" in event else None
    data = pd.concat((existing, new)).drop_duplicates(subset=subset, keep=False)

    # Replace the whole table with the new one.
    data.to_sql(
        name=event["table"],
        con=engine,
        schema=event["schema"],
        if_exists="append",
        index=False,
        method="multi",
    )
    return {
        "statusCode": 200,
        "message": f"{data.shape[0] - existing.shape[0]} rows added",
    }
