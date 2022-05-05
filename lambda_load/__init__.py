"""Load players data from Cartola FC to the database."""

import csv
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


def create_update_query(table, cols, vals, subset):
    """Create update statement."""
    set_ = ", ".join([f'"{c}" = {v}' for c, v in zip(cols, vals)])
    where = " AND ".join([f'"{c}" = {v}' for c, v in zip(cols, vals) if c in subset])
    return f"UPDATE {table} SET {set_} WHERE {where}"


def create_insert_query(table, cols, vals):
    """Create insert statement."""
    cols = ", ".join([f'"{c}"' for c in cols])
    vals = ", ".join([str(v) for v in vals])
    return f"INSERT INTO {table} ({cols}) VALUES ({vals})"


def handler(event, context=None):
    """Lambda handler."""
    data = pd.read_csv(io.StringIO(utils.aws.s3.load(event["uri"])), index_col=0)
    table = event["schema"] + "." + event["table"]

    update_count = 0
    insert_count = 0
    with engine.connect() as conn:
        for _, row in data.iterrows():
            values = (
                row.to_csv(
                    header=False,
                    index=False,
                    quoting=csv.QUOTE_NONNUMERIC,
                    quotechar="'",
                    na_rep="NULL",
                )
                .replace("'NULL'", "NULL")
                .strip()
                .split("\n")
            )

            query = create_update_query(table, row.index, values, event["subset"])
            res = conn.execute(query)
            update_count += res.rowcount
            if res.rowcount == 0:  # No match
                query = create_insert_query(table, row.index, values)
                conn.execute(query)
                insert_count += 0

    return {
        "statusCode": 200,
        "updated": update_count,
        "inserted": insert_count,
    }
