"""Transform odds data."""

import json
import os

import numpy as np
import pandas as pd

import utils.aws.s3
import utils.http


def get_odds(match):
    """Get odds."""
    data = {"home": {}, "away": {}, "draw": {}}
    for booker in match["bookmakers"]:
        for market in booker["markets"]:
            if market["key"] == "h2h":
                for outcome in market["outcomes"]:
                    if outcome["name"] == match["home_team"]:
                        data["home"][booker["key"]] = outcome["price"]
                    elif outcome["name"] == match["away_team"]:
                        data["away"][booker["key"]] = outcome["price"]
                    elif outcome["name"] == match["Draw"]:
                        data["away"][booker["key"]] = outcome["price"]
                    else:
                        raise ValueError("Invalid name")
    return data


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    # Load
    data = json.loads(utils.aws.s3.load(event["uri"]))

    # Transform
    rows = []
    for match in data:
        odds = get_odds(match)
        row = {
            "home": row["home_team"],
            "away": row["away_team"],
            "avg_home": np.mean(odds["home"].values()),
            "avg_away": np.mean(odds["away"].values()),
            "avg_draw": np.mean(odds["draw"].values()),
            "pinnacle_home": odds["home"]["pinnacle"],
            "pinnacle_away": odds["home"]["pinnacle"],
            "pinnacle_draw": odds["home"]["pinnacle"],
        }
        rows.append(row)

    # Save as CSV
    uri = os.path.splitext(event["uri"])[0] + ".csv"
    utils.aws.s3.save(data=pd.DataFrame.from_records(rows).to_csv(), uri=uri)
    return {"uri": uri}
