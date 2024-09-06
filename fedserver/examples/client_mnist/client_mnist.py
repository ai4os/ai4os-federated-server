import flwr as fl
import numpy as np
from pathlib import Path

from keras.datasets import mnist

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

import certifi

# Load and process data:
(X_train, y_train), (X_test, y_test) = mnist.load_data()

X_train = np.reshape(X_train, (60000, 28, 28, 1))
X_train = X_train.astype("float32") / 255
X_test = np.reshape(X_test, (10000, 28, 28, 1))
X_test = X_test.astype("float32") / 255
y_train = to_categorical(y_train, 10)
y_test = to_categorical(y_test, 10)

# Create a new train/test set for ONE CLIENT:
x_train = X_train[: len(X_train) // 30]
y_train = y_train[: len(X_train) // 30]

x_test = X_test[: len(X_test) // 30]
y_test = y_test[: len(X_test) // 30]

# Model to be trained:
model = Sequential()
model.add(Conv2D(32, (3, 3), activation="relu", input_shape=(28, 28, 1)))
model.add((MaxPooling2D((2, 2))))
model.add(Conv2D(64, (3, 3), activation="relu"))
model.add((MaxPooling2D((2, 2))))
model.add(Conv2D(64, (3, 3), activation="relu"))
model.add(Flatten())
model.add(Dense(64, activation="relu"))
model.add(Dense(10, activation="softmax"))
model.compile(
    loss="categorical_crossentropy", optimizer="rmsprop", metrics=["accuracy"]
)
model.summary()


# Flower client:
class Client1(fl.client.NumPyClient):
    def get_parameters(self, config):
        return model.get_weights()

    def fit(self, parameters, config):
        model.set_weights(parameters)
        model.fit(x_train, y_train, epochs=5, batch_size=32)
        return model.get_weights(), len(x_train), {}

    def evaluate(self, parameters, config):
        model.set_weights(parameters)
        loss, accuracy = model.evaluate(x_test, y_test)
        return loss, len(x_test), {"accuracy": accuracy}


# Start -> connecting with the server
# ---------------- INCLUDE THE UUID OF THE FL SERVER ---------------------------
uuid = ... # UUID of the deployment with the server
center = ... # Probably ifca or iisas
end_point = f"fedserver-{uuid}.{center}-deployments.cloud.ai4eosc.eu" # Update if needed
# ------------------------------------------------------------------------------
fl.client.start_client(
    server_address=f"{end_point}:443",
    client=Client1().to_client(),
    root_certificates=Path(certifi.where()).read_bytes(),
)
