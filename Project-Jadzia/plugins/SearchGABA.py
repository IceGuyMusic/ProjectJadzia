""" This is a extension for Jadzia to search for GABA in an mzML File """

from pyopenms import *
import pandas as pd
import plotly.express as px
from dataclasses import dataclass, field
import factory
from returnData import ReturnData


@dataclass 
class SearchGABA:
    name: str
    exp: MSExperiment
    returnDF: ReturnData = field(init=False)

    def run(self, obj) -> ReturnData:
        self.exp = obj.exp
        mz = 104.1 
        rt = 26.0

        for spectrum in self.exp:
            if spectrum.getMSLevel() == 2 and abs(spectrum.getPrecursors()[0].getMZ() - mz) < 0.1:
                if abs(spectrum.getRT() - rt)<5.0 :
                    retention_time = spectrum.getRT()
                    peaks = [(peak.getMZ(), peak.getIntensity()) for peak in spectrum]
        print(peaks)
        target_mz = [45.0356, 43.0201, 69.0348, 86.0615, 87.0452, 104.08]
        tolerance = 0.1 / 100

        filtered_peaks = []
        for peak in peaks:
            for mz in target_mz:
                if abs(peak[0] - mz) / mz <= tolerance:
                    filtered_peaks.append(peak)
                    break
        data = {"mz": [], "intensity": []}
        
        # Hinzufügen der gefilterten Peaks zum Dictionary
        for peak in filtered_peaks:
            data["mz"].append(peak[0])
            data["intensity"].append(peak[1])
        
        # Erstellen des Pandas-Dataframes aus dem Dictionary
        obj.df = pd.DataFrame(data)
        print(obj.df.head)
        return obj

def initialize() -> None:
    factory.register("SearchGABA", SearchGABA)
