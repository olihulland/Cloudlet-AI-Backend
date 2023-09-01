from threading import Thread
from ML.model_converter import convertModelToTFlite, convertModelToTFJS
from ML.model_trainer import train_model
import os

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

    def doConversion(self) -> None:
        convertModelToTFlite()

    def trainModel(self, data: dict, id: str) -> None:
        m, hist = train_model(data);
        convertModelToTFJS(m, id)
        return hist

    def modelExists(self, id: str) -> bool:
        return os.path.exists(f"ML/ConvertToTFJS/{id}")
    
    def removeModelFile(self, id: str, fileName: str) -> None:
        os.system(f"rm -f ML/ConvertToTFJS/{id}/{fileName}")
        # if the folder is empty, remove it
        if len(os.listdir(f"ML/ConvertToTFJS/{id}")) == 0:
            os.system(f"rm -rf ML/ConvertToTFJS/{id}")
    
    def run(self):
        print("--- RUNNING ML CONTROLLER ---")
