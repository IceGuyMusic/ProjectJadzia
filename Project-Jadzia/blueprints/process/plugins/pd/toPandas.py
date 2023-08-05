
@dataclass
class Spectra:
    exp: MSExperiment
    filename: str
    curr_path: str = app.config['MZML_FOLDER']
    nrOfSpectra: int = field(init=False)
    filepath: str = field(init=False)
    ms_level: List[int] = field(default=None)
    precursor: List[float] = field(default=None)
    rt: List[float] = field(default=None)
    products: List[float] = field(default=None)
    peaks: List[float] = field(default=None)

    def __post_init__(self):
        self.filepath = os.path.join(self.curr_path, self.filename)
        MzMLFile().load(self.filepath, self.exp) 
        self.nrOfSpectra = self.exp.getNrSpectra() 

        self.ms_level = []
        self.precursor = []
        self.rt = []
        self.products = []
        self.peaks = []

        self.createDF()

    def createDF(self):
        for i in range(self.nrOfSpectra):
            Spec = self.exp[i]
            self.ms_level.append(Spec.getMSLevel())
            if Spec.getPrecursors():
                Prec = Spec.getPrecursors()
                list_Prec = []
                for i in Prec:
                    list_Prec.append(i.getMZ())
                self.precursor.append(list_Prec)
            else:
                self.precursor.append(None)
            self.rt.append(Spec.getRT())
            if Spec.getProducts():
                Prod = Spec.getProducts()
                list_Prod = []
                for i in Prod:
                    list_Prod.append(i.getMZ())
                self.products.append(list_Prod) 
            else:
                self.products.append(None)
            self.peaks.append(Spec.get_peaks())
        
        data = {
            'ms_level': self.ms_level,
            'precursor': self.precursor,
            'rt' : self.rt,
            'products' : self.products,
            'peaks' : self.peaks
        }    
        self.DF = pd.DataFrame(data)

