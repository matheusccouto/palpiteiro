"""Load players data from Cartola FC to the database."""

import io
import os

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

import utils.aws.s3
import utils.cockroachdb

LOCATION = "us-east4"

creds = service_account.Credentials.from_service_account_info(
    info={
        "type": os.environ["GCP_TYPE"],
        "project_id": os.environ["GCP_PROJECT_ID"],
        "private_key_id": os.environ["GCP_PRIVATE_KEY_ID"],
        "private_key": os.environ["GCP_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": os.environ["GCP_CLIENT_EMAIL"],
        "client_id": os.environ["GCP_CLIENT_ID"],
        "auth_uri": os.environ["GCP_AUTH_URI"],
        "token_uri": os.environ["GCP_TOKEN_URI"],
        "auth_provider_x509_cert_url": os.environ["GCP_AUTH_PROVIDER_X509_CERT_URL"],
        "client_x509_cert_url": os.environ["GCP_CLIENT_X509_CERT_URL"],
    }
)
client = bigquery.Client(
    project=creds.project_id, location="us-east4", credentials=creds
)


def create_match_query(table, cols, vals, subset):
    """Create update statement."""
    set_ = ", ".join([f'"{c}" = {v}' for c, v in zip(cols, vals)])
    where = " AND ".join([f'"{c}" = {v}' for c, v in zip(cols, vals) if c in subset])
    return f"UPDATE {table} SET {set_} WHERE {where}"


def create_match_query(table, cols, vals, subset):
    """Create update statement."""
    set_ = ", ".join([f'"{c}" = {v}' for c, v in zip(cols, vals)])
    where = " AND ".join([f'"{c}" = {v}' for c, v in zip(cols, vals) if c in subset])
    return f"UPDATE {table} SET {set_} WHERE {where}"


def create_insert_query(cols):
    """Create insert statement."""
    cols = ", ".join([f"{c}" for c in cols])
    return f"INSERT ({cols}) VALUES ({cols})"


def handler(event, context=None):
    """Lambda handler."""
    data = pd.read_csv(io.StringIO(utils.aws.s3.load(event["uri"])), index_col=0) + 6
    table = event["schema"] + "." + event["table"]
    tmp_table = event["schema"] + ".tmp_" + event["table"]

    data.to_gbq(
        destination_table=tmp_table,
        project_id=os.environ["GCP_PROJECT_ID"],
        if_exists="replace",
        credentials=creds,
    )
    cols = ",".join(data.columns)
    match = " AND ".join([f"a.{col} = b.{col}" for col in event["subset"]])
    update = ", ".join([f"a.{col} = b.{col}" for col in data.columns])

    query = f"""
    MERGE {table} a
    USING {tmp_table} b
        ON {match}
    WHEN MATCHED THEN
        UPDATE SET {update}
    WHEN NOT MATCHED THEN
        INSERT ({cols}) VALUES ({cols})
    """
    job = client.query(query, location=LOCATION, project=os.environ["GCP_PROJECT_ID"])

    return {
        "statusCode": 200,
        # "message": job.result()._total_rows,
    }
