#!/usr/bin/env python
# Flask
from flask import Flask, redirect, url_for, render_template, send_file, request, session, flash
from flask_sqlalchemy import SQLAlchemy
# Celery
from tasks.celery import make_celery
from celery import Celery
from celery.result import AsyncResult
# Datenprocessierung und Verarbeitung
from pyopenms import *
from datetime import timedelta
import datetime
import os
import pickle
import pandas as pd
import plotly.express as px
# Eigene 
from main.config import Config

from dataclasses import dataclass, field

# Hello Darkness
db = SQLAlchemy()

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
    app.register_blueprint(main)
    app.register_blueprint(upload)
    app.register_blueprint(process)
    app.register_blueprint(results)
    db.init_app(app)
    with app.test_request_context():
        db.create_all()
    return app

app = create_app()

celery = make_celery(app)

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
        new_study = study(name, date, matrix, os.getcwd(), method_data_prcs)
        new_study.save_class()
        flash('Study saved successfully!')
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
            results = generateTIC.delay(os.getcwd(), filename, True)
            flash("Celery is working to produce TIC")
        elif modus == "MS1":
            results = showMS1.delay(os.getcwd(), filename)
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
#                                                                              #
#                                Celery Tasks                                  #
#                                                                              #
#                                                                              #
################################################################################

@celery.task(name='Jadzia.generateTIC')
def generateTIC(curr_path, filename, GausFilter):
    New_Workflow = Workflow(curr_path, filename)
    exp = MSExperiment() 
    MzMLFile().load(New_Workflow.get_path(), exp)
    if GausFilter:
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
    return f"Save {filename}"

@celery.task(name='Jadzia.showMS1')
def showMS1(curr_dir, filename):
    Workflow_class = Workflow(curr_dir, filename)
    exp = MSExperiment()
    MzMLFile().load(Workflow_class.get_path(), exp)
    df = pd.DataFrame(columns=['mz', 'intensity', 'rt'])
    n = exp.getNrSpectra() # Nummer wie viele Experimente ich hatte
    i=0
    while i < n:
        data = {
            'mz' : exp[i].get_peaks()[0], 
            'intensity' : exp[i].get_peaks()[1],
            'rt' : exp[i].getRT()
        }
        df_data = pd.DataFrame(data)
        df = pd.concat([df, df_data])
        i=i+1
    #df = df.query('rt < 300 & rt > 50')
    fig = px.line(df, x="mz", y="intensity", line_group="rt", title='MS1 Spektrum')
    Workflow_class.save_as_pickle(fig, True)
    return f"Save and ready"

################################################################################
#                                                                              #
#                                                                              #
#                           Notwendige Funktionen                              #
#                                                                              #
#                                                                              #
################################################################################

class Workflow:
    def __init__(self,curr_path:str,  name: str):
        self.name = name
        self.curr_path = curr_path

    def get_path(self):
        self.path = os.path.join(self.curr_path,"uploads", "mzml", self.name)
        return str(self.path)

    def save_as_pickle(self, df, MSMS=False):
        if MSMS:
            filename = f"{self.name}_MSMS.dax"
        else:
            filename = f"{self.name}.dax"
        with open(f"{self.curr_path}/uploads/process/{filename}", 'wb') as f:
            pickle.dump(df, f)

    def save_class(self):
        with open(f"{self.curr_path}/uploads/process/{self.name}.workflow", 'wb') as f:
            pickle.dump(self, f)

    def load_class(self):
        """ load a class from pickle """

@dataclass
class study:
    """ this dataclass descripes a study. Which methods are included, wich files and other metadata """
    name: str
    date: datetime.datetime # Have to be a datetime modell
    matrix: str # species, or matrix e.g. Homo Sapiens Blood
    curr_path: str
    method_data_prcs: str # 
    measurements: list[str] = field(default_factory=list)

    def save_class(self):
        with open(f"{self.curr_path}/uploads/process/{self.name}.study", 'wb') as f:
            pickle.dump(self, f)

    def load_class(self):
        with open(f"{self.curr_path}/uploads/process/{self.name}.study", 'wb') as f:
            self = pickle.load(f)

    def get_all_methods() -> list[str]:
        """ read all possible methods from a json file and return a list """

    def add_measurement(self, new_mess) -> list[str]:
        return self.measurement.append(new_mess)
    
    def delete_measurement(self, del_mess) -> list[str]:
        return self.measurement.remove(del_mess)

def FilterGauss(exp, gaussian_width=1.0):
    gf = GaussFilter()
    param = gf.getParameters()
    param.setValue("gaussian_width", gaussian_width)
    gf.setParameters(param)
    gf.filterExperiment(exp)
    print("Filtered data")
    return exp

def get_mzml_files():
    mzml_files = []
    for file in os.listdir("./uploads/mzml/"):
        if file.endswith('.mzML'):
            mzml_files.append(file)
    return mzml_files

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

