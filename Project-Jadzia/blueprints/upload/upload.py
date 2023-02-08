#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename
import os

upload = Blueprint('upload', __name__)

@upload.route("/upload/", methods=['POST', 'GET'])
def func_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            flash(f"Successfull upload for file {filename}")
            convert_wiff(file_path)
            return render_template('main.html')
    return render_template('upload.html') 

@upload.route("/uploadWindows/", methods=['POST', 'GET'])
def WINupload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files or 'scan' not in request.files:
            flash('No file or scan part')
            return redirect(request.url)
        file = request.files['file']
        scan = request.files['scan']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '' or scan.filename == '':
            flash('No selected file or scan')
            return redirect(request.url)
        if file and scan and allowed_file(file.filename) and allowed_file(scan.filename):
            filename = secure_filename(file.filename)
            scan_filename = secure_filename(scan.filename)
            file_path = current_app.config['WIN_UPLOAD_FOLDER'] + str(filename)
            scan_path = current_app.config['WIN_UPLOAD_FOLDER'] + str(scan_filename)
            file.save(file_path)
            scan.save(scan_path)
            flash(f"Successfull upload for file {filename} and scan {scan_filename}")
            WIN_convert_wiff(file_path)
            return render_template("main.html")
    return render_template('upload.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def convert_wiff(file_path):
    from main.config import bash_msconvert
    os.system(f"%s %s -o %s " % (bash_msconvert, file_path, current_app.config['MZML_FOLDER']))

def WIN_convert_wiff(file_path):
    from main.config import windows_msconvert
    os.system(f"%s %s -o %s " % (windows_msconvert, file_path, current_app.config['WIN_MZML_FOLDER']))
    flash('File converted')

