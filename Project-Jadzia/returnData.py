""" This is a class for the return object of the plugins. That is neccessary because to transfer the modified data in an other method and to allow not only MS Data  """

from pyopenms import *
from dataclasses import dataclass
import pandas as pd

@dataclass
class ReturnData:
    exp: MSExperiment
    df: pd.DataFrame
    error: bool = False
    msg_err: str = ""

