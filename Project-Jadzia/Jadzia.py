#!/usr/bin/env python

from flask import Flask, redirect, url_for, render_template, send_file, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from main.config import Config
from tasks.celery import make_celery
from celery import Celery

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.secret_key = "YC!NWN"
    app.config.from_object(Config)
    app.config.update(CELERY_CONFIG={
        'broker_url': 'redis://localhost:6379',
        'result_backend': 'redis://localhost:6379',
    })
    app.permanent_session_lifetime = timedelta(days = 3)
    from main.main import main
    app.register_blueprint(main)
    db.init_app(app)
    with app.test_request_context():
        db.create_all()
    return app

app = create_app()

app.config.update(CELERY_CONFIG={
    'broker_url': 'redis://localhost:6379',
    'result_backend': 'redis://localhost:6379',
})
celery = make_celery(app)

@app.route("/")
def mainPage():
    return render_template("main.html")

@app.route("/celery/")
def addd_API():
    add_together.delay(1,12)
    return "Send a Celery"


@celery.task(name='Jadzia.add_together')
def add_together(a,b):
    results = a + b
    return results


if __name__ == "__main__":
    app.run(debug=True)

