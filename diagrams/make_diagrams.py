"""Create README.md overview diagram."""

# pylint: disable=expression-not-assigned,pointless-statement

import os

from diagrams import Diagram
from diagrams.aws.integration import StepFunctions
from diagrams.custom import Custom
from diagrams.gcp.analytics import Bigquery
from diagrams.gcp.storage import Storage
from diagrams.gcp.compute import Functions
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import Users


THIS_DIR = os.path.dirname(__file__)
ICONS_DIR = os.path.join(THIS_DIR, "icons")


with Diagram(
    filename=os.path.join(THIS_DIR, "architecture"),
    show=False,
    # curvestyle="curved",
    direction="LR",
):

    cartola = Custom("cartola", os.path.join(ICONS_DIR, "cartola.png"))
    express = Custom("cartola express", os.path.join(ICONS_DIR, "express.png"))
    fivethirtyeight = Custom("fivethirtyeight", os.path.join(ICONS_DIR, "538.png"))
    odds = Custom("the-odds-api", os.path.join(ICONS_DIR, "the_odds_api.png"))
    streamlit = Custom("streamlit", os.path.join(ICONS_DIR, "streamlit.png"))
    bigquery = Bigquery("bigquery")
    draft = StepFunctions("draft")
    bot = StepFunctions("bot")
    users = Users("users")
    train = GithubActions("train")
    store = Storage("model store")
    remote = Functions("remote function")

    # ETLs
    cartola >> StepFunctions("players") >> bigquery
    cartola >> StepFunctions("scouts") >> bigquery
    cartola >> StepFunctions("matches") >> bigquery
    fivethirtyeight >> StepFunctions("spi") >> bigquery
    odds >> StepFunctions("odds") >> bigquery

    # Backend
    bigquery >> draft
    draft >> bot
    bot >> cartola

    # Frontend
    draft >> streamlit
    streamlit >> users
    users >> cartola
    users >> express

    # Machine Learning
    bigquery >> train
    train >> store
    store >> remote
    remote >> bigquery
