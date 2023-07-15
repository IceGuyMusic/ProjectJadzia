#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename
import os

flash_messages = {
    'no_file_or_scan': 'No file or scan part',
    'no_selected_file_or_scan': 'No selected file or scan',
}

upload = Blueprint('upload', __name__)

@upload.route("/", methods=['POST', 'GET'])
def uploadFile():
    if request.method == 'POST':
        
        file = request.files['file']
        scan = request.files['scan']

        # check if upload is a HPLC file 
        if hplc_file(file.filename):
            file_path = current_app.config['HPLC_FOLDER']+ str(file.filename)
            file.save(file_path)
            flash(f"Successfull upload for file {file.filename}")
            current_app.logger.warning(f"{file.filename} was uploaded")
            return render_template("main.html")

        # check if scan is also part of the upload
        if 'file' not in request.files or 'scan' not in request.files:
            flash_message('no_file_or_scan')
            return redirect(request.url)
        
        if file.filename == '' or scan.filename == '':
            flash_message('no_selected_file_or_scan')
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

def flash_message(key):
    if key in flash_messages:
        flash(flash_messages[key])
    else:
        flash('Unknown ErrorCode: {}'.format(key))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def hplc_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS_HPLC']

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

