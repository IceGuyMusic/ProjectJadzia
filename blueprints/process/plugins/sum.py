""" This is a extension for Jadzia to add some other pipelines """

from dataclasses import dataclass
import factory

def count():
    n = 1+2
    print(n)

@dataclass
class sumData: 
    name: str

    def run(self) -> None:
        print("ABC... One Two Three!!")
        count()

def initialize() -> None:
    factory.register("sum", sumData)


