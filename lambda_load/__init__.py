"""Load players data from Cartola FC to the database."""

import io
import json
import os
import time

import numpy as np
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

import utils.aws.s3

LOCATION = "us-east4"
DTYPES = {
    "INTEGER": pd.Int64Dtype(),
    "FLOAT": "float64",
    "STRING": pd.StringDtype(),
    "BOOLEAN": pd.BooleanDtype(),
}

creds = service_account.Credentials.from_service_account_info(
    info={
        "type": os.environ["GCP_SERVICE_ACCOUNT_TYPE"],
        "project_id": os.environ["GCP_SERVICE_ACCOUNT_PROJECT_ID"],
        "private_key_id": os.environ["GCP_SERVICE_ACCOUNT_PRIVATE_KEY_ID"],
        "private_key": os.environ["GCP_SERVICE_ACCOUNT_PRIVATE_KEY"].replace(
            "\\n", "\n"
        ),
        "client_email": os.environ["GCP_SERVICE_ACCOUNT_CLIENT_EMAIL"],
        "client_id": os.environ["GCP_SERVICE_ACCOUNT_CLIENT_ID"],
        "auth_uri": os.environ["GCP_SERVICE_ACCOUNT_AUTH_URI"],
        "token_uri": os.environ["GCP_SERVICE_ACCOUNT_TOKEN_URI"],
        "auth_provider_x509_cert_url": os.environ[
            "GCP_SERVICE_ACCOUNT_AUTH_PROVIDER_X509_CERT_URL"
        ],
        "client_x509_cert_url": os.environ["GCP_SERVICE_ACCOUNT_CLIENT_X509_CERT_URL"],
    }
)
client = bigquery.Client(
    location=LOCATION,
    credentials=creds,
)


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    table = f"{creds.project_id}.{event['schema']}.{event['table']}"
    tmp_table = f"{creds.project_id}.{event['schema']}.tmp_{event['table']}"

    table_schema = {
        field.name: DTYPES[field.field_type] for field in client.get_table(table).schema
    }
    file = utils.aws.s3.load(event["uri"])
    data = pd.read_csv(io.StringIO(file), index_col=0).astype(table_schema)
    data.to_gbq(
        destination_table=tmp_table,
        if_exists="replace",
        credentials=creds,
        location=LOCATION,
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
    job = client.query(query, location=LOCATION)

    while not job.done():
        time.sleep(0.1)

    if job.errors:
        raise RuntimeError(json.dumps(job.errors))

    client.delete_table(tmp_table)
    return {
        "statusCode": 200,
        "num_affected_rows": job.num_dml_affected_rows,
    }
