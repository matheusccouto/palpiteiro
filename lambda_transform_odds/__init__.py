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
                    elif outcome["name"] == "Draw":
                        data["draw"][booker["key"]] = outcome["price"]
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
            "season": int(match["commence_time"][:4]),
            "timestamp": match["commence_time"],
            "home": match["home_team"],
            "away": match["away_team"],
            "avg_home": np.mean(list(odds["home"].values())),
            "avg_away": np.mean(list(odds["away"].values())),
            "avg_draw": np.mean(list(odds["draw"].values())),
            "max_home": np.max(list(odds["home"].values()), initial=np.nan),
            "max_away": np.max(list(odds["away"].values()), initial=np.nan),
            "max_draw": np.max(list(odds["draw"].values()), initial=np.nan),
            "pinnacle_home": odds["home"].get("pinnacle"),
            "pinnacle_away": odds["away"].get("pinnacle"),
            "pinnacle_draw": odds["draw"].get("pinnacle"),
        }
        rows.append(row)

    # Save as CSV
    uri = os.path.splitext(event["uri"])[0] + ".csv"
    utils.aws.s3.save(data=pd.DataFrame.from_records(rows).to_csv(index=False), uri=uri)
    return {"uri": uri}
