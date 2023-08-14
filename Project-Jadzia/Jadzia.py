#!/usr/bin/env python
# Flask
from flask import Flask, redirect, url_for, render_template, send_file, request, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user 
# Celery
from tasks.celery import make_celery
from celery.result import AsyncResult
# Datenprocessierung und Verarbeitung
from pyopenms import *
from datetime import timedelta
import pandas as pd
import plotly.express as px
# Eigene 
from main.config import Config
from dataclasses import dataclass, field, asdict
import json, bcrypt, os, pickle, datetime
from typing import List
from model import User
from celery import Celery, Task

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

def create_app(config_class=Config):
    app = Flask(__name__)
    app.secret_key = "YC!NWN"
    app.config.from_object(Config)
    app.config.update(CELERY={
        'broker_url': 'redis://redis:6379/0',
        'result_backend': 'redis://redis:6379/0',
    })
    app.permanent_session_lifetime = timedelta(days = 3)
    from main.main import main
    from blueprints.upload.upload import upload
    from blueprints.process.process import process
    from blueprints.results.results import results
    from blueprints.study.study import study
    from blueprints.login.login import Login
    app.register_blueprint(main)
    app.register_blueprint(Login)
    app.register_blueprint(upload, url_prefix='/upload')
    app.register_blueprint(study, url_prefix='/study')
    app.register_blueprint(process, url_prefix='/ConfigAnalyses')
    app.register_blueprint(results)
    celery_init_app(app)
    return app


app = create_app()
celery = app.extensions["celery"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with open(app.config['DB_USERS'], 'r') as f:
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


@app.route('/dashboard')
def dashboard():
    from blueprints.process.process import load_dataframe_from_pickle
    df = load_dataframe_from_pickle(app.config['DB_REPORTS'])
    return render_template('dashboard.html', db_reports = df.to_html())

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
