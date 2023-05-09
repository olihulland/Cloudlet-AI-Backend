"""
Class responsible for parsing the message recieved in the serial monitor.
"""

import json

class SerialData:
    def __init__(self, message: str) -> None:
        self.data_list = self.parseMessage(message)

    def __str__(self) -> str:
        return "\nLEN: " + str(len(self.data_list)) + "\nDATA:\n" + str(self.data_list)

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