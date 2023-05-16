"""
Class responsible for parsing the message recieved in the serial monitor.
"""

import json

class SerialData:
    def __init__(self, message: str, classification: int | None, deviceID: str, uniqueID: str) -> None:
        self._data_list = self.parseMessage(message)
        self._classification = classification
        self._deviceID = deviceID
        self._uniqueID = uniqueID

    def __str__(self) -> str:
        return "\nLEN: " + str(len(self._data_list)) + "\nCLASS: " + str(self._classification) + "\nDATA:\n" + str(self._data_list)

    def parseMessage(self, message: str) -> list[dict]:
        message = message.strip()
        asList = message.split("}{")
        toReturn = []
        for data in asList:
            d = data.strip("{}")
            try:
                asDict = json.loads(("{" + d + "}").encode('unicode_escape'))
                toReturn.append(asDict)
            except json.decoder.JSONDecodeError:
                print(f"INVALID JSON: {d}")
                continue

        return toReturn
    
    def toDict(self) -> dict:
        return {
            "data": self._data_list,
            "classification": self._classification,
            "deviceID": self._deviceID,
            "uniqueID": self._uniqueID
        }
    
    @property
    def data(self) -> list[dict]:
        return self._data_list
    
    @property
    def deviceID(self) -> str:
        return self._deviceID
    
    @property
    def uniqueID(self) -> str:
        return self._uniqueID
    
    @property
    def classification(self) -> str:
        return self._classification