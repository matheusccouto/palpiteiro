"""Transform players data from Cartola FC."""

import json
import os

import pandas as pd

import utils.aws.s3
import utils.http


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    # Load
    data = json.loads(utils.aws.s3.load(event["uri"]))

    # Transform
    data = data["atletas"]
    for row in data:
        row.update(row.pop("scout"))

        if "scouts" in row["gato_mestre"]:
            row["gato_mestre"].pop("scouts")
        row.update(row.pop("gato_mestre"))

    # Save as CSV
    uri = os.path.splitext(event["uri"])[0] + ".csv"
    utils.aws.s3.save(data=pd.DataFrame.from_records(data).to_csv(index=False), uri=uri)
    return {"uri": uri}
