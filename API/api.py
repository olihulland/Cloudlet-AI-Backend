from flask import Flask, Response
from flask_cors import CORS
from flask_sock import Sock
from Data.data_controller import DataController
import json

app = Flask(__name__)
CORS(app)
sock = Sock(app)

DATA_CONTROLLER = DataController.getInstance()

@app.get("/test")
def get_test():
    return "Hello World! :)"

@app.get("/data")
def get_data():
    data = json.dumps(DATA_CONTROLLER.data)
    return Response(data, mimetype="application/json")

@sock.route("/monitor-data")
def monitor_data(ws):
    while True:
        if (DATA_CONTROLLER._data_updated):
            data = json.dumps({"updatedQueries": ["getData"]})
            ws.send(data)
            DATA_CONTROLLER.reset_data_updated()