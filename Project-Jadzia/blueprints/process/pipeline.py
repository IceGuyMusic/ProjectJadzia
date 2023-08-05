from typing import Protocol
from blueprints.process.returnData import ReturnData

class DataPipeline(Protocol):
    def run(self) -> ReturnData:
        """ run the pipe """
