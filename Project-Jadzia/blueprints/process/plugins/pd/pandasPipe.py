

@dataclass
class FilterRT:
    DF: pd.DataFrame
    minRT: float 
    maxRT: float

    def run(self) -> pd.DataFrame:
        filterDF = self.DF.query("rt > @self.minRT & rt < @self.maxRT ")
        return  filterDF.copy()

@dataclass
class FilterMSLevel:
    DF: pd.DataFrame
    MSLevel_Filter: int

    def run(self) -> pd.DataFrame:
        filterDF = self.DF.query("ms_level == @self.MSLevel_Filter")
        return filterDF.copy()

@dataclass
class FilterPrecursor:
    DF: pd.DataFrame
    minPrecIon: float
    maxPrecIon: float

    def run(self) -> pd.DataFrame:
        filterDF = self.DF.query("precursor > @self.minPrecIon & precursor < @self.maxPrecIon")
        return filterDF.copy()

