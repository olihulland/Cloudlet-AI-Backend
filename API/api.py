from flask import Flask, Response
from flask_cors import CORS
from Data.data_controller import DataController
from flask_socketio import SocketIO
import json

app = Flask(__name__)
CORS(app)
socket_ = SocketIO(app, cors_allowed_origins="*")

DATA_CONTROLLER = DataController.getInstance()

def run(debug):
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