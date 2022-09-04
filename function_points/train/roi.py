"""ROI modelling"""

# %%

import pandas as pd

df = pd.read_gbq("SELECT * FROM express.historico")
df.head()

# %%

df["rodada"] = df["competicao"].str.extract(r"((?![Rd\s])\d+(?=:))").astype(int)
df.head()

# %%

MAX = {
    24: 146.58,
    23: 119.35,
}

df["max"] = df["rodada"].apply(lambda x: MAX[x])
df.head()

# %%

df["pontuacao_norm"] = df["pontuacao"] / df["max"]
df.head()

# %%

import numpy as np

df["roi"] = df["premiacao"] / 10
df["roi_log"] = np.log(df["roi"])
df.head()

# %%
from sklearn.linear_model import LinearRegression

X_train = df[["pontuacao_norm"]]
y_train = df["roi"]

model = LinearRegression()
model.fit(X_train, y_train)

# %%

import plotly.express as px

px.line(df, x="pontuacao_norm", y="roi_log", color="rodada")
