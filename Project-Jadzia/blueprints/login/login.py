#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename
import os, json, bcrypt
from model import User

Login = Blueprint('Login', __name__)



@Login.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('Login.register')) 

        # Überprüfen, ob der Benutzername und die E-Mail-Adresse eindeutig sind
        if password_Ver != password:
            flash('Beide Passwörter stimmen nicht miteinander überein!', 'error')
            return redirect(url_for('Login.register'))
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

@Login.route('/Login', methods=['GET', 'POST'])
def login_bf():
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

