#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename
import os


main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template('base.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main.route("/upload/", methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            convert_wiff(file_path)
            return f"Succesfull upload for file {filename}"
    return render_template('upload.html') 


@main.route("/download/<name>")
def download_file(name):
    from flask import send_from_directory
    return send_from_directory(current_app.config['MZML_FOLDER'], name)

def convert_wiff(file_path):
    from main.config import bash_msconvert
    os.system(f"%s %s -o %s " % (bash_msconvert, file_path, current_app.config['MZML_FOLDER']))

@main.route('/<name>')
def error(name):
    return f"{name} was not found"
