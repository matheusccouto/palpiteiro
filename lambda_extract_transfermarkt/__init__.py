"""Extract transfermarkt data from kaggle."""

import datetime
import glob
import os

import kaggle

import utils.aws.s3

kaggle.api.authenticate()


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    kaggle.api.dataset_download_files(
        dataset="davidcariboo/player-scores",
        path="/tmp/transfermarkt",
        force=True,
        unzip=True,
    )

    bucket = os.environ["BUCKET"]
    week = datetime.datetime.now().strftime("%y-%V")

    uri_list = []
    for path in glob.glob("/tmp/transfermarkt/*.csv"):
        key = f"{week}/{os.path.basename(path)}"
        uri = f"s3://{bucket}/{key}"
        with open(path, encoding="utf-8") as file:
            utils.aws.s3.save(data=file.read(), uri=uri)
        uri_list.append({"uri": uri})

    return uri_list
