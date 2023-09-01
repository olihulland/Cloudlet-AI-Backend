# Cloudlet-AI-Backend
Backend built in python for my SCC321 Project.

The backend is responsible for three main things:

1. Communicating with the micro:bit "Cloudlet Hub" over serial - receiving data from the micro:bit, handshakes, sending ident commands, etc. The data collected here is stored in the 'database' - this is actually a simple data structure stored using the python pickle module.

2. Hosting a REST-ish API for the frontend to communicate with. This API is used to access the data stored in the 'database', and to communicate to the backend for ML model training and conversion (see below).

3. Doing ML model training and conversion. See section below for more details.

## How to run
1. Install using poetry
```bash
poetry install
```

**Note: only tested on MacOS with M1 - you may need to alter the tensorflow dependencies in the pyproject.toml file to get it to work on your system. (Used tensorflow-macos for M1 compatibility)**

2. Run using poetry
```bash
poetry run python main.py <port_for_serial>
```
e.g. `poetry run python main.py /dev/tty.usbmodem4302`

## Notes on ML model training

Responsible for model training and conversion.

### Conversion

The tensorflow js model is converted to a tensorflow model using [`tensorflowjs.converters`](https://github.com/tensorflow/tfjs-converter/blob/master/tfjs-converter/python/tensorflowjs/converters/keras_tfjs_loader.py). This is then converted to a tflite model using [`tensorflow.lite.TFLiteConverter`](https://www.tensorflow.org/api_docs/python/tf/lite/TFLiteConverter). This is then returned to the fronted for use in the makecode extension/microbit.

### Training

Really, I would like training to be done in browser using tensorflow.js but I came across bugs doing this - see the [frontend repo](https://github.com/olihulland/Cloudlet-AI-Frontend) for more details. It would be possible to do this in future and then only use the backend for conversion.

The model training is done using tensorflow. Requests are sent to the API and then the code in `model_trainer.py' is used. The request is given in the following format:

```typescript
{
  features: number[][];
  labels: number[];
  model: {
    layers: {
      type: string;
      units: number;
      activation: string;
    }[];
    compile: {
      optimizer:
        | string
        | {
            type: string;
            learningRate: number;
          };
      loss: string;
      metrics?: string[];
    };
    fit: {
      epochs: number;
      batchSize?: number;
    };
  };
}
```

This means that the model structure can be defined in the frontend. For example, I used this:

```typescript
    model: {
        layers: [
        {
            type: "dense",
            units: 20,
            activation: "relu",
        },
        {
            type: "dense",
            units: 10,
            activation: "relu",
        },
        {
            type: "dense",
            units: numClasses,
            activation: "softmax",
        },
        ],
        compile: {
            optimizer: {
                type: "adam",
                learningRate: 0.001,
            },
            loss: "categorical_crossentropy",
            metrics: ["accuracy"],
        },
        fit: {
            epochs: epochs,
            batchSize: 32,
        },
    }
```

Currently the backend only supports dense layers and the adam optimizer.

## Notes on the serial protocol

The microbit api only supports sending strings over radio of up to 18 characters. To overcome this limitation a simple protocol is used. It is not great and work could be done to improve it - particularly using the json isn't great but was an easy way to be extensible.

The protocol is as follows:

1. Student microbit sends handshake request to cloudlet with serial number and class label of recording.

    `HS<serialNum>,<classLabelNum>`

2. Cloudlet microbit hub recieves and passes to Serial controller via serial. This allocates a two char alphanumeric code for the transmission of this recording. This is sent back to the student microbit via radio from the hub.

    `HS<serialNum>,<ID e.g. aa>`

3. Student microbit sends data in 18 char transmissions as individual jsons. The recording is terminated by a semi-colon. Each transmission has a sequence number.

    `<ID>0,{"n":0,"x":123`

    `<ID>1,4,"y":-23,"z":2`
    
    `<ID>2,3,"s":1}{"n":1`
    
    `...`
    
    `<ID>345,"s":1034};`