"""Read data from Google Big Query."""

import json
from decimal import Decimal

import pandas as pd
from pandas import Timestamp

import utils.google

creds = utils.google.get_creds_from_env_vars()


class Encoder(json.JSONEncoder):
    """Encoder for JSON."""

    def default(self, o):
        """Encode Decimal."""
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, Timestamp):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    dic = pd.read_gbq(
        query=event["query"],
        project_id=creds.project_id,
        index_col=None,
        credentials=creds,
    ).to_dict(orient="records")
    return json.loads(json.dumps(dic, cls=Encoder))
