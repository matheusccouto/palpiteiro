"""Create README.md diagrams."""

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import StepFunctions
from diagrams.aws.storage import S3
from diagrams.generic.blank import Blank
from diagrams.gcp.analytics import Bigquery

THIS_DIR = os.path.dirname(__file__)




with Diagram(filename=os.path.join(THIS_DIR, "test"), show=False, curvestyle="ortho"):

    with Cluster("step function: cartola players"):
        (
            Blank("/atletas/mercado")
            >> Lambda("extract")
            >> S3("JSON")
            >> Lambda("transform")
            >> S3("CSV")
            >> Lambda("load bigquery")
            >> Bigquery("cartola.atletas")
        )
    
    with Cluster("step function: cartola scouts"):
        (
            Blank("/atletas/pontuados")
            >> Lambda("extract")
            >> S3("JSON")
            >> Lambda("transform")
            >> S3("CSV")
            >> Lambda("load bigquery")
            >> Bigquery("cartola.pontuados")
        )

    with Cluster("step function: cartola matches"):
        (
            Blank("/partidas")
            >> Lambda("extract")
            >> S3("JSON")
            >> Lambda("transform")
            >> S3("CSV")
            >> Lambda("load bigquery")
            >> Bigquery("cartola.partidas")
        )

    with Cluster("step function: fivethirtyeight spi"):
        (
            Blank("/soccer-api/club")
            >> Lambda("extract")
            >> S3("CSV")
            >> Lambda("load bigquery")
            >> Bigquery("fivethirtyeight.spi")
        )


with Diagram(filename=os.path.join(THIS_DIR, "test2"), show=False, curvestyle="ortho"):

    load_gbq = Lambda("load bigquery")


    cartola = Blank("Cartola")
    fivethirtyeight = Blank("FiveThirtyEight")

    with Cluster("ETLs"):

        with Cluster("step function: cartola players"):
            
            s3_players = S3("cartola players")
            extract_players = Lambda("extract")
            transform_players = Lambda("transform")

            cartola >> extract_players
            extract_players >> Edge(label="JSON") >> s3_players
            extract_players >> transform_players
            transform_players >> Edge(label="CSV") >> s3_players
            transform_players >> load_gbq

        with Cluster("step function: cartola scouts"):
            
            s3_scouts = S3("cartola scouts")
            extract_scouts = Lambda("extract")
            transform_scouts = Lambda("transform")

            cartola >> extract_scouts
            extract_scouts >> Edge(label="JSON") >> s3_scouts
            extract_scouts >> transform_scouts
            transform_scouts >> Edge(label="CSV") >> s3_scouts
            transform_scouts >> load_gbq

        with Cluster("step function: cartola matches"):
            
            s3_matches = S3("cartola matches")
            extract_matches = Lambda("extract")
            transform_matches = Lambda("transform")

            cartola >> extract_matches
            extract_matches >> Edge(label="JSON") >> s3_matches
            extract_matches >> transform_matches
            transform_matches >> Edge(label="CSV") >> s3_matches
            transform_matches >> load_gbq
        
        with Cluster("step function: fivethirtyeight spi"):
            
            s3_spi = S3("fivethirtyeight spi")
            extract_spi = Lambda("extract")

            fivethirtyeight >> extract_spi
            extract_spi >> Edge(label="CSV") >> s3_spi
            extract_spi >> load_gbq

    gbq = Bigquery("palpiteiro")
    load_gbq >> gbq

    with Cluster("step function: draft"):
            
        read_gbq = Lambda("read bigquery")
        draft = Lambda("draft")

        gbq >> read_gbq >> draft

    streamlit = Blank("Streamlit")
    draft >> streamlit