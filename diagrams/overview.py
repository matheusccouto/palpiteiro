"""Create README.md overview diagram."""

# pylint: disable=expression-not-assigned

import os

from diagrams import Cluster, Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import StepFunctions
from diagrams.aws.mobile import APIGateway
from diagrams.aws.storage import S3
from diagrams.custom import Custom
from diagrams.gcp.analytics import Bigquery
from diagrams.gcp.compute import Functions
from diagrams.gcp.storage import Storage

THIS_DIR = os.path.dirname(__file__)
ICONS_DIR = os.path.join(THIS_DIR, "icons")


with Diagram(
    filename=os.path.join(THIS_DIR, "overview"),
    show=False,
    curvestyle="curved",
):

    cartola = Custom("cartola", os.path.join(ICONS_DIR, "cartola.png"))
    fivethirtyeight = Custom("fivethirtyeight", os.path.join(ICONS_DIR, "538.png"))
    warehouse = Bigquery("big query")
    streamlit = Custom("streamlit", os.path.join(ICONS_DIR, "streamlit.png"))

    cartola >> StepFunctions("players") >> warehouse
    cartola >> StepFunctions("scouts") >> warehouse
    cartola >> StepFunctions("matches") >> warehouse
    fivethirtyeight >> StepFunctions("spi") >> warehouse
    Functions("machine learning") - warehouse
    warehouse >> StepFunctions("genetic algorithm") >> APIGateway("API") >> streamlit


with Diagram(
    "\nCartola Players",
    filename=os.path.join(THIS_DIR, "state-machine-cartola-players"),
    show=False,
    curvestyle="curved",
):
    with Cluster("state machine"):
        extract = Lambda("extract")
        json = S3("json")
        transform = Lambda("transform")
        csv = S3("csv")
        load = Lambda("load")
    (
        Custom("/atletas/mercado", os.path.join(ICONS_DIR, "cartola.png"))
        >> extract
        >> json
        >> transform
        >> csv
        >> load
        >> Bigquery("cartola\natletas")
    )


with Diagram(
    "\nCartola Scouts",
    filename=os.path.join(THIS_DIR, "state-machine-cartola-scouts"),
    show=False,
    curvestyle="curved",
):
    with Cluster("state machine"):
        extract = Lambda("extract")
        json = S3("json")
        transform = Lambda("transform")
        csv = S3("csv")
        load = Lambda("load")
    (
        Custom("/atletas/pontuados", os.path.join(ICONS_DIR, "cartola.png"))
        >> extract
        >> json
        >> transform
        >> csv
        >> load
        >> Bigquery("cartola\npontuados")
    )


with Diagram(
    "\nCartola Matches",
    filename=os.path.join(THIS_DIR, "state-machine-cartola-matches"),
    show=False,
    curvestyle="curved",
):
    with Cluster("state machine"):
        extract = Lambda("extract")
        json = S3("json")
        transform = Lambda("transform")
        csv = S3("csv")
        load = Lambda("load")
    (
        Custom("/partidas", os.path.join(ICONS_DIR, "cartola.png"))
        >> extract
        >> json
        >> transform
        >> csv
        >> load
        >> Bigquery("cartola\npartidas")
    )


with Diagram(
    "\nFiveThirtyEight SPI",
    filename=os.path.join(THIS_DIR, "state-machine-fivethirtyeight-spi"),
    show=False,
    curvestyle="curved",
):
    with Cluster("state machine"):
        extract = Lambda("extract")
        json = S3("json")
        transform = Lambda("transform")
        csv = S3("csv")
        load = Lambda("load")
    (
        Custom("/soccer-api/club", os.path.join(ICONS_DIR, "538.png"))
        >> extract
        >> json
        >> transform
        >> csv
        >> load
        >> Bigquery("fivethirtyeight\nspi")
    )


with Diagram(
    "\Big Query",
    filename=os.path.join(THIS_DIR, "big-query"),
    show=False,
    curvestyle="curved",
):
    step_functions_cartola_players = StepFunctions("cartola players")
    step_functions_cartola_scouts = StepFunctions("cartola scouts")
    step_functions_cartola_matches = StepFunctions("cartola matches")
    step_functions_538_spi = StepFunctions("fivethirtyeight spi")
    points = Functions("predict points")

    with Cluster("big query"):
        cartola_atletas = Bigquery("cartola\natletas")
        cartola_pontuados = Bigquery("cartola\npontuados")
        cartola_partidas = Bigquery("cartola\npartidas")
        dim_club = Bigquery("cartola\ndim_club")
        dim_position = Bigquery("cartola\ndim_position")
        dim_status = Bigquery("cartola\ndim_status")
        stg_atletas_player = Bigquery("cartola\nstg_atletas_player")
        stg_atletas_scoring = Bigquery("cartola\nstg_atletas_scoring")
        stg_partidas_match = Bigquery("cartola\nstg_partidas_match")
        stg_pontuados_scoring = Bigquery("cartola\nstg_pontuados_scoring")
        dim_player = Bigquery("cartola\ndim_layer")
        fct_match = Bigquery("cartola\nfct_match")
        fct_scoring = Bigquery("cartola\nfct_scoring")

        fivethirtyeight_spi = Bigquery("fivethirtyeight\nspi")
        dim_slug = Bigquery("fivethirtyeight\ndim_slug")
        stg_spi_match = Bigquery("fivethirtyeight\nstg_spi_match")
        fct_spi = Bigquery("fivethirtyeight\nfct_spi")

        fct_club = Bigquery("palpiteiro\nfct_club")
        fct_player = Bigquery("palpiteiro\nfct_player")
        dim_player_last = Bigquery("palpiteiro\ndim_player_last")

    step_functions_cartola_players >> cartola_atletas
    step_functions_cartola_scouts >> cartola_pontuados
    step_functions_cartola_matches >> cartola_partidas
    step_functions_538_spi >> fivethirtyeight_spi

    cartola_atletas >> stg_atletas_player
    cartola_atletas >> stg_atletas_scoring
    cartola_pontuados >> stg_pontuados_scoring
    cartola_partidas >> stg_partidas_match
    fivethirtyeight_spi >> stg_spi_match

    stg_atletas_player >> dim_player
    stg_partidas_match >> fct_match
    dim_club >> fct_match
    stg_spi_match >> fct_spi
    dim_slug >> fct_spi
    dim_club >> fct_scoring
    dim_player >> fct_scoring
    stg_atletas_scoring >> fct_scoring
    stg_pontuados_scoring >> fct_scoring
    dim_position >> fct_scoring
    dim_status >> fct_scoring
    fct_match >> fct_club
    fct_spi >> fct_club
    fct_scoring >> fct_club
    fct_club >> fct_player
    fct_scoring >> fct_player
    fct_match >> dim_player_last
    fct_player >> dim_player_last

    Storage("model\n(gradient boosting)") >> points
    points >> dim_player_last

    dim_player_last >> StepFunctions("draft")


with Diagram(
    "\Draft",
    filename=os.path.join(THIS_DIR, "state-machine-draft"),
    show=False,
    curvestyle="curved",
):
    with Cluster("state machine"):
        read = Lambda("read")
        draft = Lambda("draft\n(genetic algo)")
    (Bigquery("big query") >> read >> draft >> APIGateway("api"))
