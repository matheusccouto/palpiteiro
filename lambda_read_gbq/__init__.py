"""Read data from Google Big Query."""

import pandas as pd

import utils.google

creds = utils.google.get_creds_from_env_vars()


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    return pd.read_gbq(
        query=event["query"],
        project_id=creds.project_id,
        index_col=None,
        credentials=creds,
    ).to_dict(orient="records")
