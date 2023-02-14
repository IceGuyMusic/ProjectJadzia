#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename
import os

upload = Blueprint('upload', __name__)

@upload.route("/", methods=['POST', 'GET'])
def uploadFile():
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
            file_path = current_app.config['WIFF_FOLDER']+ str(filename)
            scan_path = current_app.config['WIFF_FOLDER'] + str(scan_filename)
            file.save(file_path)
            scan.save(scan_path)
            flash(f"Successfull upload for file {filename} and scan {scan_filename}")
            convert_wiff(file_path)
            current_app.logger.info(f"{filename} was uploaded")
            return render_template("main.html")
        else:
            flash("Cannot save file. Maybe wrong type")
            current_app.logger.warning(f"{file.filename} or {scan.filename} or both  was blocked because not allowed extension")
            return redirect(request.url)
    return render_template('upload.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def convert_wiff(file_path):
    from main.config import bash_msconvert
    import platform 
    plt = platform.system()
    if plt == "Windows":
        WIN_convert_wiff(file_path)
    elif plt == "Linux":
        os.system(f"%s %s -o %s " % (bash_msconvert, file_path, current_app.config['MZML_FOLDER']))
        flash('File was converted in mzML')
    else: 
        flash('Convert was mot supported!')

def WIN_convert_wiff(file_path):
    from main.config import windows_msconvert
    os.system(f"%s %s -o %s " % (windows_msconvert, file_path, current_app.config['MZML_FOLDER']))
    flash('File converted')

