"""Extract players data from Cartola FC."""

import csv
import io
import json
import os

import utils.aws.s3
import utils.http


def handler(event, context=None):
    """Lambda handler."""
    data = json.loads(utils.aws.s3.load(event["uri"]))
    data = data["atletas"]  # Filter relevant key.

    output = io.StringIO()
    writer = csv.DictWriter(output, data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)

    uri = os.path.splitext(event["uri"])[0] + ".csv"
    utils.aws.s3.save(data=output.read().encode(), uri=uri)
    return {"uri": uri}
