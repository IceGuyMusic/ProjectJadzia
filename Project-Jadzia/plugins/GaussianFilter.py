""" This is a extension for Jadzia to Filter a OpenMS Experiment"""

from dataclasses import dataclass
import factory
from pyopenms import *
from returnData import ReturnData
import pandas as pd

def FilterGauss(exp, gaussian_width=1.0) -> MSExperiment:
    gf = GaussFilter()
    param = gf.getParameters()
    param.setValue("gaussian_width", gaussian_width)
    gf.setParameters(param)
    gf.filterExperiment(exp)
    print("Filtered data")
    return exp

@dataclass 
class GaussianFilter:
    name: str
    exp: MSExperiment
    returnDF: ReturnData = field(init=False)

    def run(self) -> ReturnData:
        print('Start filter...')
        filtered_exp = FilterGauss(self.exp)
        self.returnDF = ReturnData(exp=filtered_exp, df=pd.DataFrame(data=None, columns=full_df.columns, index=full_df.index))
        return self.returnDF

def initialize() -> None:
    factory.register("GaussianFilter", GaussianFilter)
