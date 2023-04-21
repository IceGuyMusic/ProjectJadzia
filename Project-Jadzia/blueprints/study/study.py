#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
import os, datetime
from dataclasses import dataclass

study = Blueprint('study', __name__)

@study.route('/create_study', methods=['GET', 'POST'])
def create_study():
    if request.method == 'GET':
        return render_template('study.html')
    elif request.method == 'POST':
        name = request.form['name']
        date_str = request.form.get('date')
        if date_str:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date = datetime.datetime.now()
        matrix = request.form['matrix']
        method_data_prcs = request.form['method_data_prcs']
        measurements = request.form['measurements']
        new_study = study_cls(name, date, matrix, current_app.config['PROCESS_FOLDER'], method_data_prcs)
        new_study.add_measurement(measurements)
        new_study.save_class()
        flash('Study saved successfully!')
        return redirect(url_for('mainPage'))

@study.route('/<filename>')
def see_study(filename):
    new_study = load_class(current_app.config['PROCESS_FOLDER'], filename)
    print(new_study)
    return redirect(url_for('mainPage'))



@dataclass
class study_cls:
    """ this dataclass descripes a study. Which methods are included, wich files and other metadata """
    name: str
    date: datetime.datetime # Have to be a datetime modell
    matrix: str # species, or matrix e.g. Homo Sapiens Blood
    curr_path: str 
    method_data_prcs: str # 
    #measurements: list[str] = field(default_factory=list)

    def save_class(self):
        with open(f"{self.curr_path}/uploads/process/{self.name}.study", 'wb') as f:
            pickle.dump(self, f)

def load_class(curr_path, filename):
    with open(f"{curr_path}/uploads/process/{filename}", 'rb') as f:
        pickl_class = pickle.load(f)
    return pickl_class

