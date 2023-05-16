from API import api
from Serial.serial_controller import SerialController
from ML.ml_controller import MLController
import sys
import threading

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <serial_port>")
        exit(1)

    debug = True

    # Start the API in a separate thread
    threading.Thread(target=lambda: api.run(debug)).start()

    # Start ML controller in a separate thread
    ml_controller = MLController.getInstance()
    ml_controller.start()

    # Start serial controller in a separate thread
    serial_port = sys.argv[1]
    serial_controller = SerialController.getInstance()
    serial_controller.initialise(serial_port)
    serial_controller.start()