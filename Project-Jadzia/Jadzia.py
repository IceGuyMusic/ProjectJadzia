#!/usr/bin/env python

from flask import Flask, redirect, url_for, render_template, send_file, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from main.config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.secret_key = "YC!NWN"
    app.config.from_object(Config)
    app.permanent_session_lifetime = timedelta(days = 3)
    from main.main import main
    app.register_blueprint(main)
    db.init_app(app)
    with app.test_request_context():
        db.create_all()
    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

