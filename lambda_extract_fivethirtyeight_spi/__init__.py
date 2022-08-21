"""Extract players data from Cartola FC."""

import datetime
import os
import zoneinfo

import pandas as pd

import utils.aws.s3
import utils.http

SPI_URL = "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches_latest.csv"
STATUS_URL = "https://api.cartola.globo.com/mercado/status"


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    now = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/Sao_Paulo"))

    status = utils.http.get(STATUS_URL)
    if status["game_over"]:
        raise ConnectionAbortedError("Extraction aborted. Game is over.")

    data = pd.read_csv(SPI_URL)
    data = data[data["league_id"] == 2105]

    bucket = os.environ["BUCKET"]
    key = f"spi/{now}.csv"
    uri = f"s3://{bucket}/{key}"
    utils.aws.s3.save(data=data.to_csv(index=False), uri=uri)
    return {"uri": uri}
