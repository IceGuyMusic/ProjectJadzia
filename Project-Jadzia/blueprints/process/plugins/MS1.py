""" This is a extension for Jadzia to Pot all MS1 Experiments in a OpenMS Experiment"""

from dataclasses import dataclass, field
from blueprints.process import factory
from pyopenms import *
from blueprints.process.returnData import ReturnData
import pandas as pd

@dataclass 
class MS1:
    name: str
    exp: MSExperiment
    returnDF: ReturnData = field(init=False)

    def run(self, obj) -> ReturnData:
        self.exp = obj.exp
        df = pd.DataFrame(columns=['mz', 'intensity', 'rt'])
        n = self.exp.getNrSpectra() 
        i=0
        while i < n:
            data = {
                'mz' : self.exp[i].get_peaks()[0], 
                'intensity' : self.exp[i].get_peaks()[1],
                'rt' : self.exp[i].getRT()
            }
            df_data = pd.DataFrame(data)
            df = pd.concat([df, df_data])
            i=i+1
        obj.fig = px.line(df, x="mz", y="intensity", line_group="rt", title='MS1 Spektrum')
        return obj

def initialize() -> None:
    factory.register("MS1", MS1)
