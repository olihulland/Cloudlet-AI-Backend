from tensorflowjs.converters import keras_tfjs_loader
import tensorflow as tf
import os

def convertModel():
    model = keras_tfjs_loader.load_keras_model("ML/GeneratedModel/model.json")
    
    os.system("rm -rf ML/ConvertToTfLite/model")
    os.system("rm -f ML/ConvertToTfLite/model_tflite")

    model.save("ML/ConvertToTfLite/model", save_format="tf")

    converter = tf.lite.TFLiteConverter.from_saved_model("ML/ConvertToTfLite/model")
    tflite_model = converter.convert()

    with open("ML/ConvertToTfLite/model_tflite", "wb") as f:
        f.write(tflite_model)

    os.system("xxd -n model_tflite -i ML/ConvertToTfLite/model_tflite > ML/ConvertToTflite/model.h")
    
    print("Model converted!")
