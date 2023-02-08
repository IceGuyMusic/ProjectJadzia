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

@main.route('/seeResult', methods=['GET', 'POST'])
def seeResult():
    if request.method == 'POST':
        file_name = request.form['file_name']
        file_path = f"./uploads/process/{file_name}"
        if os.path.exists(file_path):
            return redirect(url_for('main.load_from_pickle', filename=file_name))
        else:
            flash('File not found')
            return render_template('main.html')
    else:
        dax_files = get_pickle_files()
        return render_template('select_mzml_file.html', mzml_files=dax_files) 

@main.route('/seeResult/<filename>')
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


def get_mzml_files():
    mzml_files = []
    for file in os.listdir(current_app.config['WIN_MZML_FOLDER']):
        if file.endswith('.mzML'):
            mzml_files.append(file)
    return mzml_files
                              
def get_pickle_files():
    pickle_files = []
    for file in os.listdir("./uploads/process/"):
        if file.endswith('.dax'):
            pickle_files.append(file)
    return pickle_files


