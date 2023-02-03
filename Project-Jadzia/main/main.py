#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

################################################################################
#                                                                              #
#                                                                              #
# Upload und Download Methoden um die Daten von der MS zum Server zu bringen   #
#                                                                              #
#                                                                              #
################################################################################

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
            flash(f"Successfull upload for file {filename}")
            convert_wiff(file_path)
            return render_template('main.html')
    return render_template('upload.html') 

@main.route("/uploadWindows/", methods=['POST', 'GET'])
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

@main.route("/download/<name>")
def download_file(name):
    from flask import send_from_directory
    return send_from_directory(current_app.config['MZML_FOLDER'], name)

################################################################################
#                                                                              #
#                                                                              #
# Methoden um die Daten, welche im Pickle gespeichert wurden, zu visualisieren #
#                                                                              #
#                                                                              #
################################################################################

@main.route('/seePickle', methods=['GET', 'POST'])
def look_for_pickle():
    if request.method == 'POST':
        file_name = request.form['file_name']
        file_path = f"./uploads/process/{file_name}"
        if os.path.exists(file_path):
            return redirect(url_for('main.load_from_pickle', filename=file_name))
        else:
            flash('File not found')
            return render_template('main.html')
    else:
        pickle_files = get_pickle_files()
        return render_template('select_mzml_file.html', mzml_files=pickle_files) 

@main.route('/seePickle/<filename>')
def load_from_pickle(filename):
    import pickle
    with open('./uploads/process/'+filename, 'rb') as f:
        df = pickle.load(f)
    return render_template("show.html", plot=df.to_html(full_html=False))

################################################################################
#                                                                              #
#                                                                              #
#         Löschen überschüssiger mzML, wiff, oder pickle Dateien               #
#                                                                              #
#                                                                              #
################################################################################

@main.route('/delete_mzml_file', methods=['GET', 'POST'])
def delete_mzml_file():
    if request.method == 'POST':
        file_name = request.form['file_name']
        file_path = os.path.join(current_app.config['WIN_MZML_FOLDER'], file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash('File deleted successfully')
            return render_template('main.html')
        else:
            flash('File not found')
            return render_template('main.html')
    else:
        mzml_files = get_mzml_files()
        return render_template('delete_mzml_file.html', mzml_files=mzml_files)

    
################################################################################
#                                                                              #
#                                                                              #
#                           Notwendige Funktionen                              #
#                                                                              #
#                                                                              #
################################################################################

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def convert_wiff(file_path):
    from main.config import bash_msconvert
    os.system(f"%s %s -o %s " % (bash_msconvert, file_path, current_app.config['MZML_FOLDER']))

def WIN_convert_wiff(file_path):
    from main.config import windows_msconvert
    os.system(f"%s %s -o %s " % (windows_msconvert, file_path, current_app.config['WIN_MZML_FOLDER']))
    flash('File converted')

def get_mzml_files():
    mzml_files = []
    for file in os.listdir(current_app.config['WIN_MZML_FOLDER']):
        if file.endswith('.mzML'):
            mzml_files.append(file)
    return mzml_files
                              
def get_pickle_files():
    pickle_files = []
    for file in os.listdir("./uploads/process/"):
        if file.endswith('.pickle'):
            pickle_files.append(file)
    return pickle_files


