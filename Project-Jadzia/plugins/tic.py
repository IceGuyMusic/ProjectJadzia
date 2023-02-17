""" This is a extension for Jadzia to add some other pipelines """
from pyopenms import *
import pickle
import pandas as pd
import os 
import plotly.express as px
from dataclasses import dataclass
import factory


@dataclass 
class TIC:
    name: str
    curr_path: str
    filename: str
    GausFilter: bool 


    def run(self) -> None:
        generateTIC(self)

def generateTIC(TIC):
    New_Workflow = Workflow(TIC.curr_path, TIC.filename)
    exp = MSExperiment() 
    MzMLFile().load(New_Workflow.get_path(), exp)
    if TIC.GausFilter:
        exp = FilterGauss(exp)
    tic = exp.calculateTIC()
    retention_times, intensities = tic.get_peaks()
    retention_times = [spec.getRT() for spec in exp]
    intensities = [sum(spec.get_peaks()[1]) for spec in exp if spec.getMSLevel() == 1]
    
    retention_times = []
    intensities = []
    for spec in exp:
        if spec in exp:
            if spec.getMSLevel() == 1:
                retention_times.append(spec.getRT())
                intensities.append(sum(spec.get_peaks()[1]))
    df = pd.DataFrame({'retention_times': retention_times, 'intensities': intensities})
    df['retention_times_min'] = df.retention_times/60
    fig = px.line(df, x="retention_times_min", y="intensities", title=f"TIC der Datei {New_Workflow.name}", labels=dict(retention_times_min='Retentionszeit [s]', intenities='Intensität'))
    New_Workflow.save_as_pickle(fig)



class Workflow:
    def __init__(self,curr_path:str,  name: str):
        self.name = name
        self.curr_path = curr_path

    def get_path(self):
        self.path = os.path.join(self.curr_path, self.name)
        return str(self.path)

    def save_as_pickle(self, df, MSMS=False):
        if MSMS:
            filename = f"{self.name}_MSMS.dax"
        else:
            filename = f"{self.name}.dax"
        with open(f"{self.curr_path}/{filename}", 'wb') as f:
            pickle.dump(df, f)

    def save_class(self):
        with open(f"{self.curr_path}/uploads/process/{self.name}.workflow", 'wb') as f:
            pickle.dump(self, f)


def FilterGauss(exp, gaussian_width=1.0):
    gf = GaussFilter()
    param = gf.getParameters()
    param.setValue("gaussian_width", gaussian_width)
    gf.setParameters(param)
    gf.filterExperiment(exp)
    print("Filtered data")
    return exp

def initialize() -> None:
    factory.register("TIC", TIC)
