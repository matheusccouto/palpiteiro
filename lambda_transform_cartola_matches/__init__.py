"""Transform players data from Cartola FC."""

import json
import os

import pandas as pd

import utils.aws.s3
import utils.http


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    # Load
    data = json.loads(utils.aws.s3.load(event["uri"]))

    # Transform
    rows = data["partidas"]
    for row in rows:
        row["temporada"] = data["temporada"]
        row["rodada"] = data["rodada"]

        aproveitamento_mandante = row.pop("aproveitamento_mandante")
        aproveitamento_visitante = row.pop("aproveitamento_visitante")
        for i in range(6):
            row[f"aproveitamento_mandante_{i}"] = aproveitamento_mandante[-i]
            row[f"aproveitamento_visitante_{i}"] = aproveitamento_visitante[-i]

        transmissao = row.pop("transmissao")
        row["transmissao_label"] = transmissao["label"]
        row["transmissao_url"] = transmissao["url"]

    # Save as CSV
    uri = os.path.splitext(event["uri"])[0] + ".csv"
    utils.aws.s3.save(data=pd.DataFrame.from_records(rows).to_csv(index=False), uri=uri)
    return {"uri": uri}
