"""Extract odds from The Odds API."""

import datetime
import json
import os

import requests

import utils.aws.s3

URL = (
    "https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds/"
    f"?apiKey={os.environ['THE_ODDS_API_KEY']}&regions=eu&markets=h2h"
    )


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    odds = requests.get(URL, timeout=60)
    bucket = os.environ["BUCKET"]
    key = f"brasileirao/{datetime.datetime.now().isoformat()}.json"
    uri = f"s3://{bucket}/{key}"
    utils.aws.s3.save(data=json.dumps(odds.json()), uri=uri)
    return {"uri": uri}
