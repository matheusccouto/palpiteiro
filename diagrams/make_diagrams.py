"""Create README.md overview diagram."""

# pylint: disable=expression-not-assigned,pointless-statement

import os

from diagrams import Cluster, Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
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
):

    # Warehouse

    bigquery = Bigquery("bigquery")


    # ETLs

    cartola_atletas_mercado = Custom("/atletas/mercado", os.path.join(ICONS_DIR, "cartola.png"))
    cartola_atletas_pontuados = Custom("/atletas/pontuados", os.path.join(ICONS_DIR, "cartola.png"))
    cartola_partidas = Custom("/partidas", os.path.join(ICONS_DIR, "cartola.png"))
    fivethirtyeight = Custom("/soccer-api/club", os.path.join(ICONS_DIR, "538.png"))
    odds = Custom("/soccer_brazil_campeonato", os.path.join(ICONS_DIR, "the_odds_api.png"))
    load = Lambda("load")
    with Cluster("players"):
        (
            cartola_atletas_mercado
            >> Lambda("extract")
            >> S3("json")
            >> Lambda("transform")
            >> S3("csv")
            >> load
        )
    with Cluster("scouts"):
        (
            cartola_atletas_pontuados
            >> Lambda("extract")
            >> S3("json")
            >> Lambda("transform")
            >> S3("csv")
            >> load
        )
    with Cluster("matches"):
        (
            cartola_partidas
            >> Lambda("extract")
            >> S3("json")
            >> Lambda("transform")
            >> S3("csv")
            >> load
        )
    with Cluster("spi"):
        (
            fivethirtyeight
            >> Lambda("extract")
            >> S3("csv")
            >> load
        )
    with Cluster("odds"):
        (
            odds
            >> Lambda("extract")
            >> S3("json")
            >> Lambda("transform")
            >> S3("csv")
            >> load
        )
    load >> bigquery


    # Backend

    with Cluster("api"):
        draft = Lambda("Draft")
        read = Lambda("read")
        bigquery >> read >> Lambda("filter") >> Lambda("dropout") >> draft


    # Bot

    cartola_auth_time = Custom(r"/auth/time", os.path.join(ICONS_DIR, "cartola.png"))
    cartola_auth_time_salvar = Custom(r"/auth/time/salvar", os.path.join(ICONS_DIR, "cartola.png"))
    with Cluster("bot"):
        cartola_auth_time >> Lambda("budget") >> read
        draft >> Lambda("submit") >> cartola_auth_time_salvar


    # Frontend

    streamlit = Custom("streamlit", os.path.join(ICONS_DIR, "streamlit.png"))
    users = Users("users")
    cartola_web = Custom("web", os.path.join(ICONS_DIR, "cartola.png"))
    express_web = Custom("web", os.path.join(ICONS_DIR, "express.png"))

    draft >> streamlit
    streamlit >> users
    users >> cartola_web
    users >> express_web

    # Machine Learning
    remote = Functions("remote function")
    bigquery >> GithubActions("train") >> Storage("model store") >> remote
    remote >> bigquery
