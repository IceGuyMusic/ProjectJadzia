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

    def run(self) -> ReturnData:
        print('Start Noise Reduction...')
        filtered_exp = MSExperiment()
        for s in self.exp:
            if s.getMSLevel() == 1:
                nf = SignalToNoiseEstimatorMeanIterative()
                nf.init(s)
                filtered_exp.addSpectrum(s)
        print('End Noise Reduction')
        self.returnDF = ReturnData(exp=filtered_exp, df=pd.DataFrame(data=None, columns=full_df.columns, index=full_df.index))
        return self.returnDF

def initialize() -> None:
    factory.register("SignalToNoiseEstimator", SignalToNoiseEstimator)
