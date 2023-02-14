""" This is a extension for Jadzia to add some other pipelines """

from dataclasses import dataclass
import factory

@dataclass
class sumData: 
    name: str

    def run(self) -> None:
        print("ABC... One Two Three!!")

def initialize() -> None:
    factory.register("sum", sumData)
