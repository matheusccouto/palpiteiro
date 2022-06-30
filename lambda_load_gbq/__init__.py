"""Load players data from Cartola FC to the database."""

import io
import json
import os
import time

import numpy as np
import pandas as pd
from google.cloud import bigquery


import utils.aws.s3
import utils.google

DTYPES = {
    "INTEGER": pd.Int64Dtype(),
    "FLOAT": "float64",
    "STRING": pd.StringDtype(),
    "BOOLEAN": pd.BooleanDtype(),
}

creds = utils.google.get_creds_from_env_vars()
client = bigquery.Client(credentials=creds)


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    table = f"{creds.project_id}.{event['schema']}.{event['table']}"
    tmp_table = f"{creds.project_id}.{event['schema']}.tmp_{event['table']}"

    file = utils.aws.s3.load(event["uri"])
    data = pd.read_csv(io.StringIO(file), index_col=0)
    data["loaded_at"] = pd.Timestamp.now()
    table_schema = {
        field.name: DTYPES[field.field_type]
        for field in client.get_table(table).schema
        if field.name in data.columns
    }
    data.astype(table_schema).to_gbq(
        destination_table=tmp_table,
        if_exists="replace",
        credentials=creds,
    )

    cols = ", ".join(data.columns)
    match = " AND ".join([f"a.{col} = b.{col}" for col in event["subset"]])
    update = ", ".join([f"a.{col} = b.{col}" for col in data.columns])

    query = f"""
    MERGE `{table}` a
    USING `{tmp_table}` b
        ON {match}
    WHEN MATCHED THEN
        UPDATE SET {update}
    WHEN NOT MATCHED THEN
        INSERT ({cols}) VALUES ({cols})
    """
    job = client.query(query)

    while not job.done():
        time.sleep(0.1)

    if job.errors:
        raise RuntimeError(json.dumps(job.errors))

    client.delete_table(tmp_table)
    return {
        "statusCode": 200,
        "num_affected_rows": job.num_dml_affected_rows,
    }
