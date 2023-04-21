
@dataclass
class FeatureDetection:
    exp: MSExperiment
    filename: str
    curr_path: str = app.config['MZML_FOLDER']
    filepath: str = field(init=False)

    def __post_init__(self):
        self.filepath = os.path.join(self.curr_path, self.filename)
        SignalToNoise(self.filepath)
        self.filepath = os.path.join(self.curr_path, 'processed_file.mzML')
        self.exp = MSExperiment()
        options = PeakFileOptions()
        options.setMSLevels([1])
        self.bufferFile = MzMLFile()
        self.bufferFile.setOptions(options) 
        self.bufferFile.load(self.filepath, self.exp) 
    
    def run(self) -> None:
        # Prepare data loading (save memory by only
        # loading MS1 spectra into memory)
        options = PeakFileOptions()
        options.setMSLevels([1])
        fh = MzMLFile()
        fh.setOptions(options)
        
        # Load data
        self.exp.updateRanges()
        
        ff = FeatureFinder()
        ff.setLogType(LogType.CMD)
        
        # Run the feature finder
        name = "centroided"
        features = FeatureMap()
        seeds = FeatureMap()
        params = FeatureFinder().getParameters(name)
        ff.run(name, self.exp, features, params, seeds)
    
        features.setUniqueIds()
        fh = FeatureXMLFile()
        fh.store("output.featureXML", features)
        print("Found", features.size(), "features")

        f0 = features[0]
        for f in features:
            print(f.getRT(), f.getMZ())



#FilterBySpectraAndPeaks
@dataclass
class FilterSpecPeaks:
    exp: MSExperiment
    mz_start: float
    mz_end : float
    filtered: MSExperiment = field(init= False)

    def run(self):
        self.filtered = MSExperiment()
        for s in self.exp:
            if s.getMSLevel() > 1:
                filtered_mz = []
                filtered_int = []
                for mz, i in zip(*s.get_peaks()):
                    if mz > self.mz_start and mz < self.mz_end:
                        filtered_mz.append(mz)
                        filtered_int.append(i)
                s.set_peaks((filtered_mz, filtered_int))
                self.filtered.addSpectrum(s)


