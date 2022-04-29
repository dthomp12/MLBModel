import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

path = "https://raw.githubusercontent.com/dthomp12/MLBModel/master/MLBdata.csv"
df = pd.read_csv(path)

df = df.drop(["date", "awayTeam", "homeTeam"], axis=1)

# remove outliers - 35 games - 1.2%
df = df[df['ou'] - 23 < 0]
df = df[abs(df['spread']) - 20 < 0]

X_train, y_train = df.values[:, 3:], df.values[:, :3]
X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.3, random_state=52)
print(X_train.shape, X_test.shape)

n_features = X_train.shape[1]