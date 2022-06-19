"""Load players data from Cartola FC to the database."""

import pandas as pd

import utils.google

creds = utils.google.get_creds_from_env_vars()


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    return pd.read_gbq(
        query=event["query"],
        project_id=creds.project_id,
        index_col=False,
        credentials=creds,
    ).to_records(index=False)