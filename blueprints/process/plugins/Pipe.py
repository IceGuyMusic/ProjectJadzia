""" This is a extension for Jadzia to add some other pipelines """

from dataclasses import dataclass
from blueprints.process import factory

def nonsenseCounter():
    n = 0 
    while n < 100:
        print(n)
        n = n+1
        

@dataclass 
class Pipe:
    name: str

    def run(self) -> None:
        print('And I run and I run and I run...')
        nonsenseCounter()

def initialize() -> None:
    factory.register("Pipe", Pipe)
