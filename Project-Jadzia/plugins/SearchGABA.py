""" This is a extension for Jadzia to search for GABA in an mzML File """

from pyopenms import *
import pandas as pd
import plotly.self.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

        mz = 104.08
        tolerance = 0.01

        rt = []  # Retention time
        intensity = []  # Intensity

        # Fragment ions
        fragment_ions = [43.0201, 45.0356, 69.0348, 86.0615, 87.0452]

            # Create an empty DataFrame
        df = pd.DataFrame(columns=['m/z', 'RT', 'Intensity'])
    
        for fragment_ion in fragment_ions:
            rt = []  # Retention time
            intensity = []  # Intensity
            for spectrum in self.exp:
                if spectrum.getMSLevel() == 2:
                    mz_array, intensity_array = spectrum.get_peaks()
                    mask = np.abs(mz_array - fragment_ion) < tolerance
                    if np.sum(mask) > 0:
                        rt.append(spectrum.getRT() / 60.0)  # Convert to minutes
                        intensity.append(np.sum(intensity_array[mask]))
            # Add to the DataFrame
            df_temp = pd.DataFrame({'m/z': [fragment_ion]*len(rt), 'RT': rt, 'Intensity': intensity})
            df = pd.concat([df, df_temp])
    
        # Remove rows where Intensity is 0
        df = df[df['Intensity'] != 0]
        print(df.head)
    
    
        # Calculate the max and min RT and the total intensity
        rt_min = df['RT'].min()
        rt_max = df['RT'].max()
        total_intensity = df['Intensity'].sum()
    
    
        # Create a subplot for each fragment ion
        fig = make_subplots(rows=len(fragment_ions), cols=1, subplot_titles=[f'{ion} m/z' for ion in fragment_ions])
    
        for i, fragment_ion in enumerate(fragment_ions, start=1):
            df_temp = df[df['m/z'] == fragment_ion]
            fig.add_trace(go.Histogram(x=df_temp['RT'], name=f'{fragment_ion} m/z'), row=i, col=1)
    
        # Set the title and labels
        fig.update_layout(height=800, width=600, title_text='Distribution of Retention Time for Each Fragment Ion', showlegend=False)
        obj.fig = fig
        print("Search GABA complete")
        return obj

    def initialize() -> None:
        factory.register("SearchGABA", SearchGABA)
