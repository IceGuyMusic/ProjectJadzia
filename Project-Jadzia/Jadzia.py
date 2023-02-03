#!/usr/bin/env python

from flask import Flask, redirect, url_for, render_template, send_file, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from main.config import Config
from tasks.celery import make_celery
from celery import Celery
from celery.result import AsyncResult
from pyopenms import *
import os
import pickle
import pandas as pd
import plotly.subplots as sp
import plotly.express as px

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
    app.register_blueprint(main)
    db.init_app(app)
    with app.test_request_context():
        db.create_all()
    return app

app = create_app()

celery = make_celery(app)

@app.route("/")
def mainPage():
    return render_template("main.html")

@app.route("/TestData/<filename>/<modus>", methods=["GET"])
def modus(filename, modus):
    if modus == "TIC":
        results = generateTIC.delay(os.getcwd(),filename, True)
        flash("Celery is working to produce TIC")
    elif modus == "MS1":
        results = showMS1.delay(os.getcwd(),filename)
        flash("celery is working to produce MS1 Spectrum")
    else:
        flash("Modus is not registered")
    return redirect(url_for('mainPage'))

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
    New_Workflow.save_as_pickle(df)
    return f"Save {filename}"

def FilterGauss(exp, gaussian_width=1.0):
    gf = GaussFilter()
    param = gf.getParameters()
    param.setValue("gaussian_width", gaussian_width)
    gf.setParameters(param)
    gf.filterExperiment(exp)
    print("Filtered data")
    return exp

@celery.task(name='Jadzia.searchByPrecr')
def searchByPrecr(path):
    exp = MSExperiment()
    MzMLFile().load(path, exp)
    df_exp = pd.DataFrame(exp)
    # Initialisiere Dataframe
    precursor_list = {
        'precursor1': {'mz': 100, 'rt': 20, 'tolerance': 30},
        'precursor2': {'mz': 200, 'rt': 30, 'tolerance': 30}
    }

    # Initializing the dataframe to store the fragment ions
    df = pd.DataFrame(columns=['precursor', 'mz', 'intensity', 'rt'])

    ## Loop through the precursor_list
    #for precursor, values in precursor_list.items():
    #    mz = values['mz']
     #   rt = values['rt']
      #  tolerance = values['tolerance']

        # Select the data in the defined mz and rt range
       # prec_data = df_exp[(df_exp['mz'] >= mz - tolerance) & (df_exp['mz'] <= mz + tolerance) &
          #               (df_exp['RT'] >= rt - tolerance) & (df_exp['RT'] <= rt + tolerance)]

        # Add the precursor name and rt to the prec_data
  #      prec_data['precursor'] = precursor
   #     prec_data['rt'] = rt
#
        # Append the prec_data to the dataframe
 #       df = df.append(prec_data, ignore_index=True)

        # Plotting the dataframe using Plotly
  #      fig = px.scatter(df, x='mz', y='intensity', color='precursor', facet_col='precursor',
   #                      facet_col_wrap=2, height=400, title='Fragment Ion Plot')
    #filename = f"{os.path.basename(path)}_MSMS.pickle" 
    #save_as_pickle(fig, filename)
    print(df_exp.head())
    return f"Save and analyzed" #{filename}"

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

class Workflow:
    def __init__(self,curr_path:str,  name: str):
        self.name = name
        self.curr_path = curr_path

    def get_path(self):
        self.path = os.path.join(self.curr_path,"uploads", "mzml", self.name)
        return str(self.path)

    def save_as_pickle(self, df, MSMS=False):
        if MSMS:
            filename = f"{self.name}_MSMS.pickle"
        else:
            filename = f"{self.name}.pickle"
        with open(f"{self.curr_path}/uploads/process/{filename}", 'wb') as f:
            pickle.dump(df, f)

if __name__ == "__main__":
    app.run(debug=True)

