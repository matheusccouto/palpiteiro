"""Cartola bot."""

import os

import utils.http

GLBID = os.environ["GLBID"]
HEADERS = {"Content-Type": "application/json", "X-GLB-Token": GLBID}

POSITION = {
    "goalkeeper": "1",
    "fullback": "2",
    "defender": "3",
    "midfielder": "4",
    "forward": "5",
    "coach": "6",
}


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    return utils.http.post(
        "https://api.cartolafc.globo.com/auth/time/salvar",
        body={
            "esquema": 3,  # 433
            "atleta": [p["id"] for p in event["players"]],
            "capitao": max(event["players"], key=lambda p: p["points"])["id"],
            "reservas": {POSITION[p["position"]]: p["id"] for p in event["bench"]},
        },
        headers=HEADERS,
    )
