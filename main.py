from API import api
from serial_monitor import SerialMonitor
import sys
import threading

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <serial_port>")
        exit(1)

    debug = True

    # Start the API in a separate thread
    threading.Thread(target=lambda: api.run(debug)).start()

    # Start serial monitor in a separate thread
    serial_port = sys.argv[1]
    serial_monitor = SerialMonitor(serial_port)
    serial_monitor.start()