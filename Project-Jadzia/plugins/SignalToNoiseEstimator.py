""" This is a extension for Jadzia to Filter a OpenMS Experiment"""

from dataclasses import dataclass, field
import factory
from pyopenms import *
from returnData import ReturnData
import pandas as pd

@dataclass 
class SignalToNoiseEstimator:
    name: str
    exp: MSExperiment
    returnDF: ReturnData = field(init=False)

    def run(self, obj) -> ReturnData:
        print('Start Noise Reduction...')
        filtered_exp = MSExperiment()
        for s in obj.exp:
            if s.getMSLevel() == 1:
                nf = SignalToNoiseEstimatorMeanIterative()
                nf.init(s)
                filtered_exp.addSpectrum(s)
        print('End Noise Reduction')
        obj.exp= filtered_exp
        return obj

def initialize() -> None:
    factory.register("SignalToNoiseEstimator", SignalToNoiseEstimator)
