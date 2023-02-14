from typing import Protocol

class DataPipeline(Protocol):
    def run(self) -> None:
        """ run the pipe """
