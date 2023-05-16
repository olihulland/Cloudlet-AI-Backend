from flask import Flask, Response, request
from flask_cors import CORS
from Data.data_controller import DataController
from ML.ml_controller import MLController
from flask_socketio import SocketIO
import json

app = Flask(__name__)
CORS(app)
socket_ = SocketIO(app, cors_allowed_origins="*")

DATA_CONTROLLER = DataController.getInstance()
ML_CONTROLLER = MLController.getInstance()

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

    ML_CONTROLLER.flagConversion()

    return "OK"

@app.get("/model-header")
def get_model_header():
    with open("ML/ConvertToTfLite/model.h", "r") as f:
        data = f.read()
        return Response(data, mimetype="text/plain")
