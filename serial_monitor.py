from serial import Serial
from threading import Thread
import string
import uuid
from serial_data import SerialData

class SerialMonitor(Thread):
    def __init__(self, port: str):
        Thread.__init__(self)
        self.port = port
        self.idMap = {}
        self.deviceMap = {}
        self.hsMap = {}
        self.lastID = None

    def generateID(self):
        printable = string.ascii_letters + string.digits + string.punctuation.replace(",", "").replace(";", "")
        idOut = ""

        if self.lastID is None:
            idOut = printable[0] + printable[0]
        else:
            lastIndex = printable.index(self.lastID[1])
            if lastIndex == len(printable) - 1:
                firstIndex = printable.index(self.lastID[0])
                idOut = printable[(firstIndex+1) % len(printable)] + printable[0]
            else:
                idOut = self.lastID[0] + printable[lastIndex+1]

        self.lastID = idOut
        return idOut

    def run(self):
        print("--- RUNNING SERIAL MONITOR ---")

        with Serial(self.port, 115200) as ser:
            while True:
                line = ser.readline().decode().strip()

                # handshake to establish an id for transmission
                if line.startswith("HS"):
                    commaIndex = line.index(",")
                    deviceID = line[2:commaIndex]
                    recordID = line[commaIndex+1:]
                    
                    hsID = self.generateID()
                    uniqueID = str(uuid.uuid4())
                    
                    self.idMap[uniqueID] = {"hsID": hsID, "deviceID": deviceID, "recordID": recordID, "message": ""}
                    self.hsMap[hsID] = uniqueID

                    if (self.deviceMap.get(deviceID) is None):
                        self.deviceMap[deviceID] = [uniqueID]
                    else:
                        self.deviceMap[deviceID].append(uniqueID)

                    message = "HS" + deviceID + "," + hsID + "\n"

                    print(f"HS ID for {deviceID} is {hsID}")
                    ser.write((message).encode())

                elif len(line) == 0:
                    continue

                else:
                    # parse the message
                    commaIndex = line.index(",")
                    hsID = line[:2]
                    seqNum = line[2:commaIndex]
                    message = line[commaIndex+1:].strip()

                    # check if message include termination character
                    complete = False
                    if message.endswith(";"):
                        complete = True
                        message = message[:-1]
                    
                    # get the unique id
                    uniqueID = self.hsMap.get(hsID)

                    # append the message
                    self.idMap[uniqueID]["message"] += message

                    # if the message is complete, send it to the API
                    if complete:
                        data = SerialData(self.idMap[uniqueID]["message"])
                        print("API SEND: " + str(data))

