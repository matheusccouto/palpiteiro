"""Extract scouts data from Cartola FC."""

import json
import os

import utils.aws.s3
import utils.http

PLAYERS_URL = "https://api.cartola.globo.com/atletas/pontuados/{round:02d}"
STATUS_URL = "https://api.cartola.globo.com/mercado/status"


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    status = utils.http.get(STATUS_URL)
    if status["game_over"]:
        raise ConnectionAbortedError("Extraction aborted. Game is over.")

    # This endpoint returns has no reference at all for which season this is.
    # This is important to us as we work with multiseason data.
    # I'll include it inside the players that that are inside the 'atletas' key.
    season = status["temporada"]
    rnd = int(status["rodada_atual"])

    scouts = utils.http.get(PLAYERS_URL.format(round=rnd))
    if "mensagem" in scouts:
        rnd -= 1
        scouts = utils.http.get(PLAYERS_URL.format(round=rnd))

    scouts["temporada"] = season

    bucket = os.environ["BUCKET"]
    key = f"atletas/pontuados/{season}-{rnd:02d}.json"
    uri = f"s3://{bucket}/{key}"
    utils.aws.s3.save(data=json.dumps(scouts), uri=uri)
    return {"uri": uri}
