from flask import Flask

app = Flask(__name__)

@app.get("/test")
def get_test():
    return "Hello World! :)"