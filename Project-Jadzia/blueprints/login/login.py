#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename
import os

Login = Blueprint('login', __name__)

@Login.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with open(current_app.config['DB'], 'r') as f:
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

