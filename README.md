# :soccer: Palpiteiro
Fantasy soccer tips with machine learning and genetic algorithm.

[![streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://matheusccouto-palpiteiro-streamlitapp-bha1f1.streamlitapp.com)

![aws](https://img.shields.io/github/workflow/status/matheusccouto/palpiteiro/aws-main?label=aws)
![gcp](https://img.shields.io/github/workflow/status/matheusccouto/palpiteiro/gcp-main?label=gcp)
![dbt](https://img.shields.io/github/workflow/status/matheusccouto/palpiteiro/dbt-main?label=dbt)
![dbt-job](https://img.shields.io/github/workflow/status/matheusccouto/palpiteiro/dbt-job-main?label=dbt%20job)
[![dbt-docs](https://img.shields.io/github/deployments/matheusccouto/palpiteiro/github-pages?label=dbt%20docs)](https://matheusccouto.github.io/palpiteiro)
[![codecov](https://codecov.io/gh/matheusccouto/palpiteiro/branch/main/graph/badge.svg?token=jvukfL51k7)](https://app.codecov.io/gh/matheusccouto/palpiteiro/branch/main)


## Architecture Overview
![aws-card](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![gcp-card](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![python-card](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![sklearn-card](https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white) 
![streamlit-card](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![overview](diagrams/overview.png)

### Data Warehouse
The data warehouse is Google Cloud Big Query and it is built with DBT

![big-query](diagrams/dbt-lineage.png)

The model *dim_player_last* is the main one. It has all features (player, club and opponent performance) for the players available for the next round. It has a remote function (which is a Google Cloud Function) that receives these features and uses a **histogram-based gradient boosting regression tree** (sklearn version from LightGBM) to predict how many points each player will score in the next round.

You can interact with this lineage graph in the [DBT Docs](https://matheusccouto.github.io/palpiteiro).

### Backend
Gets available players (already with points predictions) for the next matches from Google Big Query and drafts the line up using a **genetic algorithm written in pure python** and returns.
![state-machine-draft](diagrams/state-machine-draft.png)

### ETLs
ETLs are AWS step functions that reads the API, saves raw data in a S3 bucket and loads into GCP Big Query.

#### Cartola Players
Players data from Cartola API comes in a nested JSON. It is stored as it is in S3, flatten into a CSV, which is also stored and finally loaded into google big query.
![state-machine-cartola-players](diagrams/state-machine-cartola-players.png)

#### Cartola Scouts
Players scouts data from Cartola API comes in a nested JSON. It is stored as it is in S3, flatten into a CSV, which is also stored and finally loaded into google big query.
![state-machine-cartola-scouts](diagrams/state-machine-cartola-scouts.png)

#### Cartola Matches
Matches data from Cartola API comes in a nested JSON. It is stored as it is in S3, flatten into a CSV, which is also stored and finally loaded into google big query.
![state-machine-cartola-matches](diagrams/state-machine-cartola-matches.png)

#### FiveThirtyEight SPI
Soccer Power Index data from FiveThirtyEight API already comes in CSV, so it just need to be stored as it is in S3 and loaded into Google Big Query.
![state-machine-fivethirtyeight-spi](diagrams/state-machine-fivethirtyeight-spi.png)


## Contact
[![Linkedin](https://img.shields.io/badge/-matheusccouto-blue?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/matheusccouto/)](https://www.linkedin.com/in/matheusccouto/)
[![Gmail](https://img.shields.io/badge/-matheusccouto@gmail.com-006bed?style=flat-square&logo=Gmail&logoColor=white&link=mailto:matheusccouto@gmail.com)](mailto:matheusccouto@gmail.com)