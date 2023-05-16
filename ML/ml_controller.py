from threading import Thread
from ML.model_converter import convertModel

class MLController(Thread):
    _instance = None
    _isConversion = False

    def __init__(self) -> None:
        Thread.__init__(self)
    
    @classmethod
    def getInstance(cls) -> "MLController":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def flagConversion(self) -> None:
        self._isConversion = True
    
    def run(self):
        print("--- RUNNING ML CONTROLLER ---")
        while True:
            if self._isConversion:
                self._isConversion = False
                print("Converting model...")
                convertModel()
                