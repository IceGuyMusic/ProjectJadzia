from typing import Protocol
from returnData import ReturnData

class DataPipeline(Protocol):
    def run(self) -> ReturnData:
        """ run the pipe """
