import tensorflow as tf
import numpy as np

def train_model(data: dict) -> tf.keras.Model:
    features = np.array(data["features"])

    # find unique labels
    uniqueLabels = set(data["labels"])
    numClasses = len(uniqueLabels)

    # one hot encode labels
    labels = tf.keras.utils.to_categorical(data["labels"], num_classes=numClasses)

    model = tf.keras.models.Sequential();
    for i, layer in enumerate(data["model"]["layers"]):
        newLayer = None
        if layer["type"] == "dense":
            if i == 0:
                newLayer = tf.keras.layers.Dense(layer["units"], activation=layer["activation"], input_shape=(len(data["features"][0]),))
            else:
                newLayer = tf.keras.layers.Dense(layer["units"], activation=layer["activation"])
        else:
            raise ValueError("Unknown layer type: " + layer["type"])
        model.add(newLayer)

    model.compile(optimizer=data["model"]["compile"]["optimizer"], loss=data["model"]["compile"]["loss"], metrics=data["model"]["compile"]["metrics"])

    model.fit(features, labels, epochs=data["model"]["fit"]["epochs"], batch_size=data["model"]["fit"]["batchSize"] if data["model"]["fit"]["batchSize"] is not None else 32)

    return model