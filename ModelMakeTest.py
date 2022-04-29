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

from keras import Model
from keras import Input
from keras.layers import Dense
from keras import metrics

# define the layers
x_in = Input(shape=(n_features,))
x1 = Dense(100, activation='relu', kernel_regularizer="l1")(x_in)
x2 = Dense(15, activation='relu', kernel_regularizer="l1")(x1)
x3 = Dense(5, activation='relu', kernel_regularizer="l1")(x2)
spread = Dense(1, name="spread", activation='linear')(x3)
# define the model
spreadModel = Model(inputs=x_in, outputs=spread)

spreadModel.compile(optimizer='adam', loss=['mse'], metrics=['mae', 'mse'])


epoch = 0
step = 1
max = 80
num_steps = max / step

epochs = np.arange(step, max, step)
test_acc = np.zeros(len(epochs))
train_acc = np.zeros(len(epochs))

for i in range(len(epochs)):
  spreadModel.fit(X_train, y_train[:,1], epochs=step, batch_size=32, verbose=0)

  #evaluate the model
  pred_train_S = spreadModel.predict(X_train)
  scores = spreadModel.evaluate(X_train, y_train[:,1], verbose = 0)
  #print(f"Accuracy on training data: {scores[1]:.3f}")

  train_acc[i] = scores[1]

  pred_train_S = spreadModel.predict(X_test)
  scores = spreadModel.evaluate(X_test, y_test[:,1], verbose = 0)
  #print(f"Accuracy on test data: {scores[1]:.3f}")

  test_acc[i] = scores[1]

import matplotlib.pyplot as plt

plt.plot(epochs, test_acc, epochs, train_acc)
plt.legend(["test", "train"])
plt.xlabel("epoch")