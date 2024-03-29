"""
A controller for storing and retrieving data.

At the moment I'm just doing this in a flat file with pickle.
"""

import pickle
import API.api as api
from datetime import datetime

INIT_DATA = {
    "record_instances": [],
    "microbits": [],
    "classes": [],
}

FILENAME = "Data/data.pickle"

class DataController:
    _instance = None

    def __init__(self) -> None:
        raise RuntimeError("Use getInstance() instead of constructor")

    def _initialise(self, filename: str) -> "DataController":
        self._filename = filename
        self._data = self._loadData()
        return self

    @classmethod
    def getInstance(cls) -> "DataController":
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._initialise(FILENAME)
        return cls._instance

    def _loadData(self) -> dict:
        try:
            with open(self._filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            # create the file
            with open(self._filename, "wb") as f:
                pickle.dump(INIT_DATA, f)
                return INIT_DATA
            
    def _saveData(self) -> None:
        with open(self._filename, "wb") as f:
            pickle.dump(self._data, f)

    @staticmethod
    def cleanRecordInstance(record_instance: dict) -> dict:
        # remove incomplete data from the record instance
        data = record_instance["data"]
        keys = []
        for instance in data:
            keys = list(instance.keys())
            for key in keys:
                if key not in keys:
                    keys.append(key)


        for instance in data:
            missing = False
            for key in keys:
                if key not in instance.keys():
                    print(f"missing key {key} in instance num {instance['n'] if 'n' in instance.keys() else 'unknown'}")
                    missing = True
            
            if missing:
                print("removing instance")
                data.remove(instance)

        toRet = record_instance.copy()
        toRet["data"] = data
        return toRet
    
    def addMicrobit(self, deviceID) -> int:
        # check if exists already
        for microbit in self._data["microbits"]:
            if microbit["deviceID"] == deviceID:
                return microbit["friendlyID"]
        
        # add new microbit
        newID = len(self._data["microbits"])
        self._data["microbits"].append({
            "deviceID": deviceID,
            "friendlyID": newID,
        })
        self._saveData()
        return newID
            
    def addRecordInstance(self, record_instance: dict) -> None:
        self.addMicrobit(record_instance["deviceID"])
        record_instance = self.cleanRecordInstance(record_instance)
        record_instance["utc"] = datetime.utcnow().isoformat()
        self._data["record_instances"].append(record_instance)
        self._saveData()
        api.broadcast_data_update()

    def deleteRecordInstance(self, recordID: str) -> bool:
        indexOfRecord = None
        classOfRecord = None
        for i, record in enumerate(self._data["record_instances"]):
            if record["uniqueID"] == recordID:
                indexOfRecord = i
                classOfRecord = record["classification"]
                break

        if indexOfRecord is None:
            return False
        
        del self._data["record_instances"][indexOfRecord]

        # remove class if no longer used
        classUsed = False
        for record in self._data["record_instances"]:
            if record["classification"] == classOfRecord:
                classUsed = True
                break
        print(f"class Used: {classUsed}")
        if not classUsed:
            for i, c in enumerate(self._data["classes"]):
                if c["id"] == str(classOfRecord):
                    print(f"removing class {c['name']}")
                    del self._data["classes"][i]
                    break

        self._saveData()
        api.broadcast_data_update()
        return True
    
    def setClass(self, classID: int, className: str) -> None:
        existing = None
        for c in self._data["classes"]:
            if c["id"] == classID:
                existing = c
                break
        if existing is not None:
            existing["name"] = className
            self._saveData()
        else:
            self._data["classes"].append({
                "id": classID,
                "name": className
            })
            self._saveData()

    def getMicrobits(self) -> list[dict]:
        return self._data["microbits"]

    @property
    def filename(self) -> str:
        return self._filename
    
    @property
    def data(self) -> dict:
        return self._data