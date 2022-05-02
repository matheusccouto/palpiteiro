"""Transform players data from Cartola FC."""

import csv
import io
import json
import os

import pandas as pd

import utils.aws.s3
import utils.http


def handler(event, context=None):
    """Lambda handler."""
    # Load
    data = json.loads(utils.aws.s3.load(event["uri"]))
    
    # Transform
    data = data["atletas"]
    for row in data:
        row.update(row.pop("scout"))

    # Save as CSV
    uri = os.path.splitext(event["uri"])[0] + ".csv"
    utils.aws.s3.save(data=pd.DataFrame.from_records(data).to_csv(), uri=uri)
    return {"uri": uri}
