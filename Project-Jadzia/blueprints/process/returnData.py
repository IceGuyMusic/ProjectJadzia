""" This is a class for the return object of the plugins. That is neccessary because to transfer the modified data in an other method and to allow not only MS Data  """

from pyopenms import *
from dataclasses import dataclass
import pandas as pd
from typing import Dict, Any
import plotly.express as px

@dataclass
class ReturnData:
    exp: MSExperiment
    df: pd.DataFrame
    fig: px.line
    error: bool = False
    msg_err: str = ""
    meta: Dict[str, Any] = None 
