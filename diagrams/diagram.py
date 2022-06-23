"""Create README.md diagrams."""

# pylint: disable=expression-not-assigned

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import StepFunctions
from diagrams.aws.storage import S3
from diagrams.custom import Custom
from diagrams.generic.blank import Blank
from diagrams.gcp.analytics import Bigquery

THIS_DIR = os.path.dirname(__file__)
ICONS_DIR = os.path.join(THIS_DIR, "icons")


with Diagram(
    "\nCartola Players",
    filename=os.path.join(THIS_DIR, "state-machine-cartola-players"),
    show=False,
):
    (
        Custom("/atletas/mercado", os.path.join(ICONS_DIR, "cartola.png"))
        >> Lambda("extract")
        >> S3("json")
        >> Lambda("transform")
        >> S3("csv")
        >> Lambda("load")
        >> Bigquery("cartola.atletas")
    )


with Diagram(
    "\nCartola Scouts",
    filename=os.path.join(THIS_DIR, "state-machine-cartola-scouts"),
    show=False,
):
    (
        Custom("/atletas/pontuados", os.path.join(ICONS_DIR, "cartola.png"))
        >> Lambda("extract")
        >> S3("json")
        >> Lambda("transform")
        >> S3("csv")
        >> Lambda("load")
        >> Bigquery("cartola.pontuados")
    )


with Diagram(
    "\nCartola Matches",
    filename=os.path.join(THIS_DIR, "state-machine-cartola-matches"),
    show=False,
):
    (
        Custom("/partidas", os.path.join(ICONS_DIR, "cartola.png"))
        >> Lambda("extract")
        >> S3("json")
        >> Lambda("transform")
        >> S3("csv")
        >> Lambda("load")
        >> Bigquery("cartola.partidas")
    )


with Diagram(
    "\nFiveThirtyEight SPI",
    filename=os.path.join(THIS_DIR, "state-machine-fivethirtyeight-spi"),
    show=False,
):
    (
        Custom("/soccer-api/club", os.path.join(ICONS_DIR, "538.png"))
        >> Lambda("extract")
        >> S3("csv")
        >> Lambda("load")
        >> Bigquery("fivethirtyeight.spi")
    )


#     with Cluster("step function: fivethirtyeight spi"):
#         (
#             Blank("/soccer-api/club")
#             >> Lambda("extract")
#             >> S3("csv")
#             >> Lambda("load bigquery")
#             >> Bigquery("fivethirtyeight.spi")
#         )


# with Diagram(filename=os.path.join(THIS_DIR, "test2"), show=False, curvestyle="ortho"):

#     load_gbq = Lambda("load bigquery")


#     cartola = Blank("Cartola")
#     fivethirtyeight = Blank("FiveThirtyEight")

#     with Cluster("ETLs"):

#         with Cluster("step function: cartola players"):

#             s3_players = S3("cartola players")
#             extract_players = Lambda("extract")
#             transform_players = Lambda("transform")

#             cartola >> extract_players
#             extract_players >> Edge(label="json") >> s3_players
#             extract_players >> transform_players
#             transform_players >> Edge(label="csv") >> s3_players
#             transform_players >> load_gbq

#         with Cluster("step function: cartola scouts"):

#             s3_scouts = S3("cartola scouts")
#             extract_scouts = Lambda("extract")
#             transform_scouts = Lambda("transform")

#             cartola >> extract_scouts
#             extract_scouts >> Edge(label="json") >> s3_scouts
#             extract_scouts >> transform_scouts
#             transform_scouts >> Edge(label="csv") >> s3_scouts
#             transform_scouts >> load_gbq

#         with Cluster("step function: cartola matches"):

#             s3_matches = S3("cartola matches")
#             extract_matches = Lambda("extract")
#             transform_matches = Lambda("transform")

#             cartola >> extract_matches
#             extract_matches >> Edge(label="json") >> s3_matches
#             extract_matches >> transform_matches
#             transform_matches >> Edge(label="csv") >> s3_matches
#             transform_matches >> load_gbq

#         with Cluster("step function: fivethirtyeight spi"):

#             s3_spi = S3("fivethirtyeight spi")
#             extract_spi = Lambda("extract")

#             fivethirtyeight >> extract_spi
#             extract_spi >> Edge(label="csv") >> s3_spi
#             extract_spi >> load_gbq

#     gbq = Bigquery("palpiteiro")
#     load_gbq >> gbq

#     with Cluster("step function: draft"):

#         read_gbq = Lambda("read bigquery")
#         draft = Lambda("draft")

#         gbq >> read_gbq >> draft

#     streamlit = Blank("Streamlit")
#     draft >> streamlit
