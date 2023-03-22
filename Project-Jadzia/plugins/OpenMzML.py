""" This is a extension for Jadzia to Filter a OpenMS Experiment"""

from dataclasses import dataclass, field
import factory
from pyopenms import *
from returnData import ReturnData
import pandas as pd
from flask import current_app

@dataclass 
class OpenMzML:
    name: str
    exp: MSExperiment
    filename: str
    #path: str = current_app.config['MZML_FOLDER'] 
    returnDF: ReturnData = field(init=False)

    def run(self, obj) -> ReturnData:
        print('Open MzML File...')
        curr_path = obj.meta['input_file_name']
        self.exp = MSExperiment()
        MzMLFile().load(curr_path, self.exp)
        obj.exp = self.exp
        return obj

def initialize() -> None:
    factory.register("OpenMzML", OpenMzML)
