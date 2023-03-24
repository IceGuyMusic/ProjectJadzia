""" This is a extension for Jadzia to Calculate the Total Ion Chromatogram for an mzML File """

from pyopenms import *
import pandas as pd
import plotly.express as px
from dataclasses import dataclass, field
import factory
from returnData import ReturnData


def generateTIC(TIC):
    tic = TIC.exp.calculateTIC()
    retention_times, intensities = tic.get_peaks()
    retention_times = [spec.getRT() for spec in TIC.exp]
    intensities = [sum(spec.get_peaks()[1]) for spec in TIC.exp if spec.getMSLevel() == 1]
    
    retention_times = []
    intensities = []
    for spec in TIC.exp:
        if spec in TIC.exp:
            if spec.getMSLevel() == 1:
                retention_times.append(spec.getRT())
                intensities.append(sum(spec.get_peaks()[1]))
    df = pd.DataFrame({'retention_times': retention_times, 'intensities': intensities})
    df['retention_times_min'] = df.retention_times/60
    fig = px.line(df, x="retention_times_min", y="intensities", title=f"TIC",  labels=dict(retention_times_min='Retentionszeit [min]', intenities='Intensität'))
    return fig

@dataclass 
class TIC:
    name: str
    exp: MSExperiment
    returnDF: ReturnData = field(init=False)

    def run(self, obj) -> ReturnData:
        self.exp = obj.exp
        tic = generateTIC(self)
        obj.fig = tic
        return obj

def initialize() -> None:
    factory.register("TIC", TIC)
