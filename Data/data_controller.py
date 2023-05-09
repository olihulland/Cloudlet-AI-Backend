"""
A controller for storing and retrieving data.

At the moment I'm just doing this in a flat file with pickle.
"""

import pickle

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
        self._data_updated = False
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
        self._data_updated = True

    @property
    def filename(self) -> str:
        return self._filename
    
    @property
    def data(self) -> dict:
        return self._data
    
    @property
    def data_updated(self) -> bool:
        return self._data_updated
    
    def reset_data_updated(self) -> None:
        self._data_updated = False