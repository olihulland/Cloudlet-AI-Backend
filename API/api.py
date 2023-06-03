from flask import Flask, Response, request
from flask_cors import CORS
from Data.data_controller import DataController
from ML.ml_controller import MLController
from Serial.serial_controller import SerialController
from flask_socketio import SocketIO
import json
import uuid

app = Flask(__name__)
CORS(app)
socket_ = SocketIO(app, cors_allowed_origins="*")

DATA_CONTROLLER = DataController.getInstance()
ML_CONTROLLER = MLController.getInstance()
SERIAL_CONTROLLER = SerialController.getInstance()

def run(debug):
    print("--- RUNNING API ---")
    socket_.run(app, debug=debug, use_reloader=False, port=5001)
    # app.run(debug=debug, use_reloader=False, port=5001)

@app.get("/test")
def get_test():
    return "Hello World! :)"

@app.get("/data")
def get_data():
    data = json.dumps(DATA_CONTROLLER.data)
    return Response(data, mimetype="application/json")

@app.get("/ident")
def get_ident():
    SERIAL_CONTROLLER.ident();
    return "",204

def broadcast_data_update():
    message = json.dumps({"queries_updated": ["getData"]})
    socket_.emit("data_update", message)

@app.delete("/data/<recordID>")
def delete_record(recordID):
    success = DATA_CONTROLLER.deleteRecordInstance(recordID)
    if success:
        return "", 204
    else:
        return "Record not found", 404

@app.post("/model")
def post_model():
    files = request.files
    print(files)
    if "model.json" not in files and "model.weights.bin" not in files:
        return "ERROR: no model files found", 400
    elif "model.json" not in files:
        return "ERROR: no model file found", 400
    elif "model.weights.bin" not in files:
        return "ERROR: no weights file found", 400
    
    modelFile = files["model.json"]
    weightsFile = files["model.weights.bin"]

    modelFile.save("ML/GeneratedModel/model.json")
    weightsFile.save("ML/GeneratedModel/model.weights.bin")

    # ML_CONTROLLER.flagConversion()
    ML_CONTROLLER.doConversion()

    with open("ML/ConvertToTfLite/model.h", "r") as f:
        data = f.read()
        return Response(data, mimetype="text/plain")

@app.post("/train")
def post_train():
    data = request.get_json()

    # generate unique id
    modelID = str(uuid.uuid4())
    
    try:
        history = ML_CONTROLLER.trainModel(data, modelID)
    except Exception as e:
        print(e)
        return str(e), 500

    # wait until folder exists before returning
    while not ML_CONTROLLER.modelExists(modelID):
        continue

    jsonResp = {"modelID": modelID, "history": history}
    return Response(json.dumps(jsonResp), mimetype="application/json")

@app.get("/trained-model/<modelID>/<fileName>")
def get_trained_model(modelID, fileName):
    if (not ML_CONTROLLER.modelExists(modelID)):
        return "Model not found", 404

    print(f"Getting {fileName} for model {modelID}")
    with open(f"ML/ConvertToTFJS/{modelID}/{fileName}", "rb") as f:
        data = f.read()
        ML_CONTROLLER.removeModelFile(modelID, fileName)
        return Response(data, mimetype="text/plain")

@app.post("/name-class/<classID>")
def post_name_class(classID):
    name = request.form["name"]
    DATA_CONTROLLER.setClass(classID, name)
    broadcast_data_update()
    return "",204

@app.get("/model-header")
def get_model_header():
    with open("ML/ConvertToTfLite/model.h", "r") as f:
        data = f.read()
        return Response(data, mimetype="text/plain")
