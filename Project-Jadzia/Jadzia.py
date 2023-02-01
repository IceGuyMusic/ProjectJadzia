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
    path = os.path.join("/home/labbikatz/ProjectJadzia/ProjectJadzia/Project-Jadzia/uploads/mzml/", filename)
    results = showMS.delay(path, True)
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
    save_as_pickle(retention_times, intensities, filename)
    return f"Save {filename}"


@celery.task(name='Jadzia.add_together')
def add_together(a,b):
    results = a + b
    return results

def save_as_pickle(retention_times, intensities, filename):
    df = pd.DataFrame({'retention_times': retention_times, 'intensities': intensities})
    with open('./uploads/process/'+filename, 'wb') as f:
        pickle.dump(df, f)

if __name__ == "__main__":
    app.run(debug=True)

