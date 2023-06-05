from serial import Serial
import serial.tools.list_ports as list_ports
from threading import Thread
import string
import uuid
from Serial.serial_data import SerialData
from Data.data_controller import DataController
from time import sleep

DATA_CONTROLLER = DataController.getInstance()

class SerialController(Thread):
    _instance = None

    def __init__(self):
        Thread.__init__(self)
        self.idMap = {}
        self.deviceMap = {}
        self.hsMap = {}
        self.lastID = None

    def initialise(self, port: str):
        self.port = port

    @classmethod
    def getInstance(cls) -> "SerialController":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

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
    
    def _sendIdent(self, deviceID: str, friendlyID: str):
        message = "ID" + deviceID + "," + friendlyID + "\n"
        print(f"Sending IDENT to {deviceID}")
        with Serial(self.port, 115200) as ser:
            ser.write(message.encode())
    
    def ident(self):
        microbits = DATA_CONTROLLER.getMicrobits()
        for microbit in microbits:
            self._sendIdent(microbit["deviceID"], str(microbit["friendlyID"]))

    def run(self):
        print("--- RUNNING SERIAL MONITOR ---")

        while True:
            portExists = False

            serialPorts = list_ports.comports()
            for serialPort in serialPorts:
                if serialPort.device.split(".")[-1] == self.port.split(".")[-1]:
                    portExists = True
                    break

            if portExists:
                try:
                    with Serial(self.port, 115200) as ser:
                        print("Connected to Cloudlet Hub")
                        while True:
                            line = ser.readline().decode().strip()

                            # handshake to establish an id for transmission
                            if line.startswith("HS"):
                                commaIndex = line.index(",")
                                deviceID = line[2:commaIndex]
                                classification = line[commaIndex+1:]
                                
                                hsID = self.generateID()
                                uniqueID = str(uuid.uuid4())
                                
                                self.idMap[uniqueID] = {"hsID": hsID, "deviceID": deviceID, "message": "", "classification": int(classification)}
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
                                    data = SerialData(self.idMap[uniqueID]["message"], self.idMap[uniqueID]["classification"], self.idMap[uniqueID]["deviceID"], uniqueID)
                                    print(f"STORE data from {self.idMap[uniqueID]['hsID']} with ID {uniqueID}")
                                    DATA_CONTROLLER.addRecordInstance(data.toDict())
                            
                            sleep(0.005)
                except OSError:
                    print("Cloudlet Hub Disconnected")

            sleep(0.005)
