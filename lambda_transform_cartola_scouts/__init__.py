"""Transform scouts data from Cartola FC."""

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
    records = []
    for key, row in data["atletas"].items():
        row["id"] = key
        row["temporada"] = data["temporada"]
        row["rodada"] = data["rodada"]
        scout = row.pop("scout")
        if scout is not None:
            row.update(scout)
        records.append(row)

    # Save as CSV
    uri = os.path.splitext(event["uri"])[0] + ".csv"
    utils.aws.s3.save(data=pd.DataFrame.from_records(records).to_csv(index=False), uri=uri)
    return {"uri": uri}
