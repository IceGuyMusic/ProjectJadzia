""" This is a extension for Jadzia to Filter a OpenMS Experiment"""

from dataclasses import dataclass, field
from typing import List
import factory
from pyopenms import *
from returnData import ReturnData
import pandas as pd


@dataclass 
class FilterByScanNr:
    name: str
    exp: MSExperiment
    scan_nrs: List[int] = field(default_factory=list)
    returnDF: ReturnData = field(init=False)

    def run(self) -> ReturnData:
        filtered_exp = MSExperiment()
        for k, s in enumerate(self.exp):
            if k in scan_nrs:
                filtered_exp.addSpectrum(s)
        self.returnDF = ReturnData(exp=filtered_exp, df=pd.DataFrame(data=None, columns=full_df.columns, index=full_df.index))
        return self.returnDF

def initialize() -> None:
    factory.register("FilterByScanNr", FilterByScanNr)
