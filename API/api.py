from flask import Flask, Response
from flask_cors import CORS
from Data.data_controller import DataController
import json

app = Flask(__name__)
CORS(app)

DATA_CONTROLLER = DataController.getInstance()

@app.get("/test")
def get_test():
    return "Hello World! :)"

@app.get("/data")
def get_data():
    data = json.dumps(DATA_CONTROLLER.data)
    return Response(data, mimetype="application/json")