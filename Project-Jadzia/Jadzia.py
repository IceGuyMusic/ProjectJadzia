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

#app.config.update(CELERY_CONFIG={
#    'broker_url': 'redis://localhost:6379',
#    'result_backend': 'redis://localhost:6379',
#})
celery = make_celery(app)


@app.route("/")
def mainPage():
    return render_template("main.html")

@app.route("/celery/")
def addd_API():
    results = add_together.delay(1,12)
    results.wait()
    flash(results.get())
    return f"Send a Celery with {results}"

@app.route("/TestData/<filename>", methods=["GET"])
def see_TestTIC(filename):
    curr_path = os.getcwd() 
    path = os.path.join(curr_path,"uploads", "mzml", filename)
    results = showMS.delay(path, True)
    flash("celery is working")
    return redirect(url_for('mainPage'))

@app.route("/MSMS/<filename>", methods=["GET"])
def searchByPrecr_sendTask(filename):
    curr_path = os.getcwd() 
    path = os.path.join(curr_path,"uploads", "mzml", filename)
    results = showMS1.delay(path)
    flash("celery is working")
    return redirect(url_for('mainPage'))

@celery.task(name='Jadzia.showMS')
def showMS(path, GausFilter):
    exp = MSExperiment() 
    MzMLFile().load(path, exp)
    if GausFilter:
        gf = GaussFilter()
        param = gf.getParameters()
        param.setValue("gaussian_width", 1.0)  # needs wider width
        gf.setParameters(param)
        gf.filterExperiment(exp)
        print("Filtered data")
        
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
    filename = f"{os.path.basename(path)}.pickle"
    df = pd.DataFrame({'retention_times': retention_times, 'intensities': intensities})
    save_as_pickle(df, filename)
    return f"Save {filename}"

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
def showMS1(path):
    exp = MSExperiment()
    MzMLFile().load(path, exp)
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
    filename = f"{os.path.basename(path)}_MSMS.pickle" 
    save_as_pickle(fig, filename)
    return f"Save and ready"


@celery.task(name='Jadzia.add_together')
def add_together(a,b):
    results = a + b
    return results

def save_as_pickle(df, filename):
    with open('./uploads/process/'+filename, 'wb') as f:
        pickle.dump(df, f)

if __name__ == "__main__":
    app.run(debug=True)

