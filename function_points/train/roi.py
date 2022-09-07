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
df["pontuacao_norm"] = (df["pontuacao_norm"] * 1000).round().astype(int)
df.head()

# %%
import numpy as np

df_resample = pd.DataFrame()
for rodada in df["rodada"].unique():
    df_uniform = pd.DataFrame({"pontuacao_norm": np.arange(1, 1000).astype(int)})
    df_uniform_rodada = df_uniform.merge(df[df["rodada"] == rodada], on="pontuacao_norm", how="left")
    df_uniform_rodada = df_uniform_rodada.fillna(method="ffill").fillna(method="bfill")
    df_resample = pd.concat((df_resample, df_uniform_rodada))

df_resample.head()

# %%

df = df_resample

df["roi"] = (df["premiacao"] - 10) / 10
df["premiacao_log1p"] = np.log1p(df["premiacao"]) 
df.tail()

# %%
from sklearn import linear_model

X_train = df[["pontuacao_norm"]]
y_train = df["premiacao_log1p"]
X_pred = np.linspace(0, 1, endpoint=True)

model = linear_model.LinearRegression()
model.fit(X_train.values, y_train.values)
y_pred = model.predict(X_pred.reshape(-1, 1))

pred_df = pd.DataFrame({"pontuacao_norm": X_pred, "premiacao": y_pred})
pred_df["rodada"] = "model"
pred_df = pd.concat((df, pred_df))

# %%

import plotly.express as px

px.scatter(pred_df, x="pontuacao_norm", y="premiacao_log1p", color="rodada")
