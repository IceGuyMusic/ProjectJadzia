""" This is a extension for Jadzia to Filter a OpenMS Experiment"""

from dataclasses import dataclass, field
from blueprints.process import factory
from pyopenms import *
from blueprints.process.returnData import ReturnData
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

    def run(self, obj) -> ReturnData:
        print('Start filter...')
        self.exp = obj.exp
        filtered_exp = FilterGauss(self.exp)
        obj.exp = filtered_exp
        return obj

def initialize() -> None:
    factory.register("GaussianFilter", GaussianFilter)
