"""
A controller for storing and retrieving data.

At the moment I'm just doing this in a flat file with pickle.
"""

import pickle
import API.api as api

INIT_DATA = {
    "record_instances": [],
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
            
    def addRecordInstance(self, record_instance: dict) -> None:
        self._data["record_instances"].append(record_instance)
        self._saveData()
        api.broadcast_data_update()

    def deleteRecordInstance(self, recordID: str) -> bool:
        indexOfRecord = None
        for i, record in enumerate(self._data["record_instances"]):
            if record["uniqueID"] == recordID:
                indexOfRecord = i
                break

        if indexOfRecord is None:
            return False
        
        del self._data["record_instances"][indexOfRecord]
        self._saveData()
        api.broadcast_data_update()
        return True

    @property
    def filename(self) -> str:
        return self._filename
    
    @property
    def data(self) -> dict:
        return self._data