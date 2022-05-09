"""Load players data from Cartola FC to the database."""

import io
import json
import os
import time

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

import utils.aws.s3

LOCATION = "us-east4"

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
    project=creds.project_id,
    location=LOCATION,
    credentials=creds,
)


def handler(event, context=None):
    """Lambda handler."""
    table = event["schema"] + "." + event["table"]
    tmp_table = event["schema"] + ".tmp_" + event["table"]

    file = utils.aws.s3.load(event["uri"])
    data = pd.read_csv(io.StringIO(file), index_col=0).convert_dtypes()
    data.to_gbq(
        destination_table=tmp_table,
        project_id=creds.project_id,
        if_exists="replace",
        credentials=creds,
        location=LOCATION,
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
    job = client.query(query, location=LOCATION, project=creds.project_id)

    while not job.done():
        time.sleep(0.1)

    if job.errors:
        raise RuntimeError(json.loads(job.errors))

    client.delete_table(tmp_table)
    return {
        "statusCode": 200,
        "num_affected_rows": job.num_dml_affected_rows,
    }
