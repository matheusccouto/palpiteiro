import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from tpot.builtins import StackingEstimator

# NOTE: Make sure that the outcome column is labeled 'target' in the data file
tpot_data = pd.read_csv("PATH/TO/DATA/FILE", sep="COLUMN_SEPARATOR", dtype=np.float64)
features = tpot_data.drop("target", axis=1)
training_features, testing_features, training_target, testing_target = train_test_split(
    features, tpot_data["target"], random_state=None
)

# Average CV score on the training set was: -15.414579276900241
exported_pipeline = make_pipeline(
    StackingEstimator(estimator=RidgeCV()),
    StandardScaler(),
    KNeighborsRegressor(n_neighbors=93, p=1, weights="distance"),
)

exported_pipeline.fit(training_features, training_target)
results = exported_pipeline.predict(testing_features)
