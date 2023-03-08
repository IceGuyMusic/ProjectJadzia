""" This is a extension for Jadzia to Centroiding a OpenMS Experiment"""

from dataclasses import dataclass, field
import factory
from pyopenms import *
from returnData import ReturnData
import pandas as pd


@dataclass 
class Centroiding:
    name: str
    exp: MSExperiment
    returnDF: ReturnData = field(init=False)

    def run(self) -> ReturnData:
        centered_exp = MSExperiment()
        PeakPickerHighRes().pickExperiment(self.exp, centered_exp, True)
        self.returnDF = ReturnData(exp=centered_exp, df=pd.DataFrame(data=None, columns=full_df.columns, index=full_df.index))
        return self.returnDF

def initialize() -> None:
    factory.register("Centroiding", Centroiding)
