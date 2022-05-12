"""Extract matches data from Cartola FC."""

import json
import os

import utils.aws.s3
import utils.http

MATCHES_URL = "https://api.cartola.globo.com/partidas"
STATUS_URL = "https://api.cartola.globo.com/mercado/status"


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    status = utils.http.get(STATUS_URL)
    if status["game_over"]:
        raise ConnectionAbortedError("Extraction aborted. Game is over.")

    matches = utils.http.get(MATCHES_URL)

    # This endpoint returns has no reference at all for which season this is.
    # This is important to us as we work with multiseason data.

    season = status["temporada"]
    rnd = matches["rodada"]

    matches["temporada"] = season

    bucket = os.environ["BUCKET"]
    key = f"partidas/{season}-{rnd:02d}.json"
    uri = f"s3://{bucket}/{key}"
    utils.aws.s3.save(data=json.dumps(matches), uri=uri)
    return {"uri": uri}
