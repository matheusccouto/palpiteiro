"""Extract players data from Cartola FC."""

import json
import os

import utils.aws.s3
import utils.http

PLAYERS_URL = "https://api.cartola.globo.com/atletas/mercado"
STATUS_URL = "https://api.cartola.globo.com/mercado/status"


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    status = utils.http.get(STATUS_URL)
    if status["game_over"]:
        raise ConnectionAbortedError("Extraction aborted. Game is over.")

    players = utils.http.get(PLAYERS_URL)

    # This endpoint returns has no reference at all for which season this is.
    # This is important to us as we work with multiseason data.
    # I'll include it inside the players that that are inside the 'atletas' key.

    season = status["temporada"]
    rnd = status["rodada_atual"]

    for player in players["atletas"]:
        player["temporada_id"] = season
        player["rodada_id"] = rnd

    bucket = os.environ["BUCKET"]
    key = f"atletas/mercado/{season}-{rnd:02d}.json"
    uri = f"s3://{bucket}/{key}"
    utils.aws.s3.save(data=json.dumps(players), uri=uri)
    return {"uri": uri}
