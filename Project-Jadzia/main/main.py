#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename
import os
from pyopenms import *

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template('main.html')


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

@main.route("/uploadWindows/", methods=['POST', 'GET'])
def WINupload():
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
            #from pathlib import Path, PureWindowsPath
            #data_folder = current_app.config['WIN_UPLOAD_FOLDER']
            #file_path_dummy = data_folder / filename
            #file_path = PureWindowsPath(file_path_dummy)
            file_path = current_app.config['WIN_UPLOAD_FOLDER'] + f"\{filename}" 
            #file_path = os.path.join(current_app.config['WIN_UPLOAD_FOLDER'], filename)
            file.save(file_path)
            WIN_convert_wiff(file_path)
            return f"Succesfull upload for file {filename}"
    return render_template('upload.html')



@main.route("/download/<name>")
def download_file(name):
    from flask import send_from_directory
    return send_from_directory(current_app.config['MZML_FOLDER'], name)

def convert_wiff(file_path):
    from main.config import bash_msconvert
    os.system(f"%s %s -o %s " % (bash_msconvert, file_path, current_app.config['MZML_FOLDER']))

def WIN_convert_wiff(file_path):
    from main.config import windows_msconvert
    os.system(f"%s %s -o %s " % (windows_msconvert, file_path, current_app.config['WIN_MZML_FOLDER']))
    flash('File converted')



@main.route("/lookData", methods=["GET"])
def see_TIC():
    exp = MSExperiment()
    MzMLFile().load(current_app.config['MZML_FOLDER'] + '/T1D_Positiv.mzML', exp)
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
    return render_template('show.html', data_1 = retention_times, data_2 = intensities)

@main.route('/<name>')
def error(name):
    flash(f"{name} was not found")
    return render_template('main.html')


@main.route('/delete_mzml_file', methods=['GET', 'POST'])
def delete_mzml_file():
  if request.method == 'POST':
    file_name = request.form['file_name']
    file_path = os.path.join(current_app.config['MZML_FOLDER'], file_name)
    if os.path.exists(file_path):
      os.remove(file_path)
      return 'File deleted successfully'
    else:
      return 'File not found'
  else:
    mzml_files = get_mzml_files()  # replace with the function that returns the list of mzML files
    return render_template('delete_mzml_file.html', mzml_files=mzml_files)

def get_mzml_files():
    mzml_files = []
    for file in os.listdir(current_app.config['MZML_FOLDER']):
        if file.endswith('.mzML'):
            mzml_files.append(file)
    return mzml_files


