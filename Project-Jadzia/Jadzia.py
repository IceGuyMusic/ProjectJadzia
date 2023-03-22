#!/usr/bin/env python
# Flask
from flask import Flask, redirect, url_for, render_template, send_file, request, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
# Celery
from tasks.celery import make_celery
from celery import Celery
from celery.result import AsyncResult
# Datenprocessierung und Verarbeitung
from pyopenms import *
from datetime import timedelta
import pandas as pd
import plotly.express as px
# Eigene 
from main.config import Config
import factory, loader
from dataclasses import dataclass, field, asdict
import json, bcrypt, os, pickle, datetime
from typing import List
from bson.objectid import ObjectId


def create_app(config_class=Config):
    app = Flask(__name__)
    app.secret_key = "YC!NWN"
    app.config.from_object(Config)
    app.config.update(CELERY_CONFIG={
        'broker_url': 'redis://localhost:6379/0',
        'result_backend': 'redis://localhost:6379/0',
    })
    app.permanent_session_lifetime = timedelta(days = 3)
    from main.main import main
    from blueprints.upload.upload import upload
    from blueprints.process.process import process
    from blueprints.results.results import results
#    from blueprints.login.login import login
    app.register_blueprint(main)
 #   app.register_blueprint(login)
    app.register_blueprint(upload, url_prefix='/upload')
    app.register_blueprint(process)
    app.register_blueprint(results)
    return app


app = create_app()
celery = make_celery(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id: int, username: str, email: str, password_hash: str):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.datetime.now()
        self.user_dict = self.to_dict()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash
        }

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with open('users.json', 'r') as f:
            users = json.load(f)

        username = request.form['username']
        password = request.form['password']

        if username not in users:
            flash('Invalid username or password')
            return redirect(url_for('login'))

        user = users[username]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            User_log = User(user['id'],user['username'], user['email'], user['password_hash'])
            login_user(User_log)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        with open('users.json', 'r') as f:
            users = json.load(f)

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_Ver = request.form['passwordVer']

        if username in users:
            flash('Username already taken')
            return redirect(url_for('register')) 

        # Überprüfen, ob der Benutzername und die E-Mail-Adresse eindeutig sind
        if password_Ver != password:
            flash('Beide Passwörter stimmen nicht miteinander überein!', 'error')
            return redirect(url_for('register'))
        else:
            # Neuen Benutzer erstellen und zur Datenbank hinzufügen

            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user = User(id(username), username, email, password_hash)
            flash('Erfolgreich registriert! Bitte melden Sie sich an.', 'success')
            users[username] = user.to_dict()
            with open('users.json', 'w') as f:
                json.dump(users, f)
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(id):
    with open('users.json', 'r') as f:
        users = json.load(f)
    # Durchlaufe alle Benutzer im Dictionary
    for user in users.values():
        if str(id) in str(user.values()):
            x= User(user.get('id'), user.get('username'), user.get('email'), user.get('password_hash'))
            return x
        else:
            return None

################################################################################
#                                                                              #
#                                                                              #
#                           Hello World und Error                              #
#                                                                              #
#                                                                              #
################################################################################

@app.route("/")
def mainPage():
    return render_template("main.html")

@app.errorhandler(404)
def page_not_found(e):
    flash('Page not found. Maybe wrong URL')
    app.logger.error('User searched for an unregistered URL')
    return render_template('main.html')

@app.route('/create_study', methods=['GET', 'POST'])
def create_study():
    if request.method == 'GET':
        return render_template('study.html')
    elif request.method == 'POST':
        name = request.form['name']
        date_str = request.form.get('date')
        if date_str:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date = datetime.datetime.now()
        matrix = request.form['matrix']
        method_data_prcs = request.form['method_data_prcs']
        measurements = request.form['measurements']
        new_study = study(name, date, matrix, app.config['PROCESS_FOLDER'], method_data_prcs)
        new_study.add_measurement(measurements)
        new_study.save_class()
        flash('Study saved successfully!')
        return redirect(url_for('mainPage'))

@app.route('/study/<filename>')
def see_study(filename):
    new_study = load_class(app.config['PROCESS_FOLDER'], filename)
    print(new_study)
    return redirect(url_for('mainPage'))

@app.route('/testArea')
def see_cwd():
    exp = MSExperiment()
    test = FeatureDetection(exp, 'T1D_Positiv.mzML')
    test.run()
    return redirect(url_for('mainPage'))

################################################################################
#                                                                              #
#                                                                              #
#                  User Interface für Aufwendige Datenanalyse                  #
#                                                                              #
#                                                                              #
################################################################################

@app.route("/DataProcessingInterface/", methods=["GET", "POST"])
def modus():
    if request.method == "POST":
        filename = request.form.get("filename")
        modus = request.form.get("modi")
        if modus == "TIC":
            results = generateTIC.delay(app.config['MZML_FOLDER'], filename, True)
            flash("Celery is working to produce TIC")
        elif modus == "MS1":
            results = showMS1.delay(app.config['MZML_FOLDER'], filename)
            flash("celery is working to produce MS1 Spectrum")
        else:
            flash("Modus is not registered")
        return redirect(url_for('mainPage'))
    else:
        filename = get_mzml_files()
        modi = ['TIC', 'MS1', 'NN']
        return render_template("Process.html", filename=filename, modi=modi)

################################################################################
#                                                                              #
#                           Notwendige Funktionen                              #
#                                                                              #
#                                                                              #
################################################################################

class sample:
    """ define samples """
    pass

class run:
    """ define a run """
    pass

class result:
    pass

class preparation:
    pass

class pipeline:
    pass

class job:
    pass

class feature:
    pass

class cluster:
    pass

@dataclass
class study:
    """ this dataclass descripes a study. Which methods are included, wich files and other metadata """
    name: str
    date: datetime.datetime # Have to be a datetime modell
    matrix: str # species, or matrix e.g. Homo Sapiens Blood
    curr_path: app.config['PROCESS_FOLDER'] 
    method_data_prcs: str # 
    #measurements: list[str] = field(default_factory=list)

    def save_class(self):
        with open(f"{self.curr_path}/uploads/process/{self.name}.study", 'wb') as f:
            pickle.dump(self, f)

def load_class(curr_path, filename):
    with open(f"{curr_path}/uploads/process/{filename}", 'rb') as f:
        pickl_class = pickle.load(f)
    return pickl_class

def get_mzml_files():
    mzml_files = []
    for file in os.listdir(app.config['MZML_FOLDER']):
        if file.endswith('.mzML'):
            mzml_files.append(file)
    return mzml_files

with open("pipeline.json") as file:
    data = json.load(file)
loader.load_plugins(data["plugins"])
some_pipes = [factory.create(item) for item in data["pipelines"]]
pipes_str = data["plugins"]

@dataclass
class HPLC_settings:
    column: str
    instrument: str
    gradient: str
    pressure: float
    flux: float
    temp: float

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

##########################################################
##########################################################

@dataclass
class DataAnalysesConfig:
    DataAnalysesID: str
    input_file_name: str
    output_file_name: str
    author: str
    run: bool = False
    list_of_methods: List[str] = field(default_factory=list)
    visitor: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

@dataclass 
class Report:
    ReportID: id
    created_by_pipe: str
    connected_data: str
    fig: px.line
    ListOfUsers: List[str] = field(default_factory=list)

def randomword(length):
    import random, string
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@app.route('/ConfigAnalyses', methods=['GET', 'POST'])
def data_form():
    if request.method == 'POST':
        data = request.form.to_dict()
        data.update({"DataAnalysesID": randomword(9)})
        data.update({"run": False})
        List_str = data.get("list_of_methods")
        List_str = List_str.replace("plugins.", "")
        methods_list = List_str.split(" | X |")
        methods_list = methods_list[:-1]
        data.update({"list_of_methods": methods_list})
        config = DataAnalysesConfig.from_dict(data)
        config.input_file_name = os.path.join(app.config['MZML_FOLDER'], config.input_file_name)
        # Speichern Sie das Config-Objekt oder fahren Sie mit der Verarbeitung fort.
        flash('Analyse is configured')
        saveDataAnalysesConfig(config)
        return redirect(url_for('mainPage')) 
    options = dict(zip(pipes_str, pipes_str))
    filename = get_mzml_files()
    return render_template('add_method.html', filename=filename, options= options)

def createDataAnalysesConfig(user_input) -> DataAnalysesConfig:
    return DataAnalysesConfig.from_dict(user_input)  

def saveDataAnalysesConfig(data: DataAnalysesConfig) -> None:
    curr_path = os.path.join(app.config['DATA_ANALYSES_CONFIG_FOLDER'], f"{data.DataAnalysesID}.json")
    with open(curr_path, 'w') as f:
        json.dump(asdict(data), f)

@app.route('/ConfigAnalyses/run/<id_url>') 
def RunDataAnalyses(id_url):
    """ User will set a DataAnalyses from route"""
    if checkID(id_url):
        run_pipeline(id_url)
        flash('Run Pipe')
        return redirect(url_for('mainPage'))
    else:
        flash('Invalid ID')
        return redirect(url_for('data_form'))

def checkID(id_url) -> bool:
    curr_path = os.path.join(app.config['DATA_ANALYSES_CONFIG_FOLDER'], f"{id_url}.json")
    file_exists = os.path.exists(curr_path)
    return file_exists

def loadDataAnalysesConfig(id_url) -> DataAnalysesConfig:
    curr_path = os.path.join(app.config['DATA_ANALYSES_CONFIG_FOLDER'], f"{id_url}.json")
    with open(curr_path) as f:
        json_obj = f.read()
    Config_dict = json.loads(json_obj)
    return createDataAnalysesConfig(Config_dict)

@celery.task(name='Jadzia.run_pipe')
def run_pipeline(id_url):
    """ run pipeline """
    if checkID(id_url) == False:
        return "Invalid ID"
    Config = loadDataAnalysesConfig(id_url)
    n = 0
    listOfMethods = [] 
    while n < len(some_pipes):
        if some_pipes[n].name in Config.list_of_methods:
            listOfMethods.append(some_pipes[n])
        n = n+1
    n = 0
    listOfMethods.reverse()
    n_max = len(listOfMethods)
    from returnData import ReturnData
    obj = ReturnData(MSExperiment(), pd.DataFrame(), meta=asdict(Config), fig = px.line())
    while n < n_max:
        print(f'run {n}')
        obj = listOfMethods[n].run(obj)
        n = n+1
    ListOfUsers = [Config.author]
    ListOfUsers.append(Config.visitor)
    outputPipe(Config.DataAnalysesID, obj, ListOfUsers)

def save_Analyses(report) -> None:
    """ save file in a dir """
    path = os.path.join(app.config['REPORT_FOLDER'], f'{report.ReportID}.rep')
    with open(path, 'wb') as f:
        pickle.dump(report, f)

def outputPipe(DataAnalysesID, obj, ListOfUsers) -> None:
    """ save mzML and create report """
    report = Report(randomword(9), created_by_pipe = DataAnalysesID, connected_data = obj.df, ListOfUsers = ListOfUsers, fig = obj.fig)
    save_Analyses(report)


    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
