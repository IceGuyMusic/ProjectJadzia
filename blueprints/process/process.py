#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename
import pandas as pd 
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import pickle, os, json
from celery import shared_task
import plotly.express as px
from blueprints.process import factory
from blueprints.process import loader
from pyopenms import *

process = Blueprint('process', __name__)

def get_pipes():
    with open(current_app.config['DB_PIPELINE']) as file:
        data = json.load(file)
    loader.load_plugins(data["plugins"])
    some_pipes = [factory.create(item) for item in data["pipelines"]]
    pipes_str = data["plugins"]
    return some_pipes, pipes_str


def get_mzml_files():
    mzml_files = []
    for file in os.listdir(current_app.config['MZML_FOLDER']):
        if file.endswith('.mzML'):
            mzml_files.append(file)
    return mzml_files

@dataclass
class DataAnalysesConfig:
    DataAnalysesID: str
    output_file_name: str
    author: str
    run: bool = False
    input_file_name: List[str] = field(default_factory=list)
    list_of_methods: List[str] = field(default_factory=list)
    visitor: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

@dataclass 
class Report:
    ReportID: id
    created_by_pipe: str
    connected_data: str
    fig: px.line
    df: pd.DataFrame
    ListOfUsers: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = { 
            "ReportID" : self.ReportID,
            "created_by_pipe" : self.created_by_pipe
               }
        if self.df.empty:
            data['df'] = '{}'
        else:
            data['df'] = self.df.to_json(orient="table")
        print(data)
        return data

@dataclass
class GreatReportJSON:
    reports: Dict[int, Dict] = field(default_factory=dict)
    first_report_id: int = None

    def add_report(self, report: Report):
        report_data = report.to_dict()
        self.reports[report.ReportID] = report_data

        if self.first_report_id is None:
            self.first_report_id = report.ReportID

    def save_to_json(self):
        if self.first_report_id is None:
            print("Error: Nothing to save")
            return

        filename = f"great_report_{self.first_report_id}.json"
        with open(filename, 'w') as f:
            json.dump(self.reports, f, indent=4)


def randomword(length):
    import random, string
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@process.route('/', methods=['GET', 'POST'])
def data_form():
    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        output_file_name = data.get("output_file_name")[0]
        id_prefix = output_file_name if output_file_name else ""
        analyses_id = randomword(9)
        data_analyses_id = f"{id_prefix}{analyses_id}" if id_prefix else analyses_id

        data.update({"output_file_name": output_file_name})
        data.update({"DataAnalysesID": data_analyses_id})
        data.update({"run": False})
        data.update({"author": data.get("author")[0]})
        List_str = data.get("list_of_methods")
        List_str = List_str[0].replace("blueprints.process.plugins.", "")
        methods_list = List_str.split(" | X |")
        methods_list = [method.strip() for method in methods_list]
        methods_list = methods_list[:-1]
        data.update({"list_of_methods": methods_list})
        config = DataAnalysesConfig.from_dict(data)
        file_name_list = []
        for n in config.input_file_name:
            file_name_list.append(os.path.join(current_app.config['MZML_FOLDER'], n))
        config.input_file_name = file_name_list 
        flash('Analyse is configured')
        saveDataAnalysesConfig(config)
        return redirect(url_for('process.seeRun')) 
    some_pipes, pipes_str = get_pipes()
    options = dict(zip(pipes_str, pipes_str))
    filename = get_mzml_files()
    return render_template('add_method.html', filename=filename, options= options)

def createDataAnalysesConfig(user_input) -> DataAnalysesConfig:
    return DataAnalysesConfig.from_dict(user_input)  

def saveDataAnalysesConfig(data: DataAnalysesConfig) -> None:
    curr_path = os.path.join(current_app.config['DATA_ANALYSES_CONFIG_FOLDER'], f"{data.DataAnalysesID}.json")
    with open(curr_path, 'w') as f:
        json.dump(asdict(data), f)

def get_config_files():
    pickle_files = []
    for file in os.listdir("./uploads/config/data_analyses/"):
        if file.endswith('.json'):
            pickle_files.append(file)
    return pickle_files

@process.route('/run/', methods=['GET', 'POST'])
def seeRun():
    if request.method == 'POST':
        id_url = request.form['file_name']
        file_path = f"./uploads/config/data_analyses/{id_url}"
        if os.path.exists(file_path):
            id_url = id_url.replace(".json", "")
            return redirect(url_for('process.RunDataAnalyses', id_url=id_url))
        else:
            flash('File not found')
            return render_template('main.html')
    else:
        config_files = get_config_files()
        return render_template('select_mzml_file.html', mzml_files=config_files) 

@process.route('/run/<id_url>') 
def RunDataAnalyses(id_url):
    """ User will set a DataAnalyses from route"""
    if checkID(id_url):
        run_pipeline.delay(id_url)
        flash('Run Pipe')
        return redirect(url_for('mainPage'))
    else:
        flash('Invalid ID')
        return redirect(url_for('process.data_form'))

def checkID(id_url) -> bool:
    curr_path = os.path.join(current_app.config['DATA_ANALYSES_CONFIG_FOLDER'], f"{id_url}.json")
    file_exists = os.path.exists(curr_path)
    return file_exists

def loadDataAnalysesConfig(id_url) -> DataAnalysesConfig:
    curr_path = os.path.join(current_app.config['DATA_ANALYSES_CONFIG_FOLDER'], f"{id_url}.json")
    with open(curr_path) as f:
        json_obj = f.read()
    Config_dict = json.loads(json_obj)
    return createDataAnalysesConfig(Config_dict)

@shared_task(name='Jadzia.run_pipe')
def run_pipeline(id_url):
    """ run pipeline """
    if checkID(id_url) == False:
        return "Invalid ID"
    Config = loadDataAnalysesConfig(id_url)
    GreatReport = []
    ForExportReport = GreatReportJSON()
    some_pipes, pipes_str = get_pipes()
    for files in Config.input_file_name:
        Config_buffer = Config
        Config_buffer.input_file_name = files
        n = 0
        listOfMethods = [] 
        while n < len(some_pipes):
            if some_pipes[n].name in Config_buffer.list_of_methods:
                listOfMethods.append(some_pipes[n])
            n = n+1
        n = 0
        #listOfMethods.reverse()
        n_max = len(listOfMethods)
        from blueprints.process.returnData import ReturnData
        obj = ReturnData(MSExperiment(), pd.DataFrame(), meta=asdict(Config_buffer), fig = px.line())
        while n < n_max:
            print(f'run {n}')
            obj = listOfMethods[n].run(obj)
            n = n+1
        ListOfUsers = [Config_buffer.author]
        ListOfUsers.append(Config_buffer.visitor)
        report = outputPipe(Config_buffer.DataAnalysesID, obj, ListOfUsers)
        GreatReport.append(report)
        ForExportReport.add_report(report)
    save_big_Analyses(GreatReport) 
    ForExportReport.save_to_json()


def save_big_Analyses(GreatReport) -> None:
    """ save file in a dir """
    path = os.path.join(current_app.config['REPORT_FOLDER'], f'{GreatReport[0].ReportID}.rep')
    with open(path, 'wb') as f:
        pickle.dump(GreatReport, f)

def save_Analyses(report) -> None:
    """ save file in a dir """
    path = os.path.join(current_app.config['REPORT_FOLDER'], f'{report.ReportID}.rep')
    with open(path, 'wb') as f:
        pickle.dump(report, f)

def outputPipe(DataAnalysesID, obj, ListOfUsers) -> Report:
    """ save mzML and create report """
    report = Report(randomword(9), created_by_pipe = DataAnalysesID, connected_data = obj.df, ListOfUsers = ListOfUsers, fig = obj.fig, df = obj.df.copy())
    create_or_load_dataframe(report)
    save_Analyses(report)
    return report

#### Ich möchte eine Funktion haben, welche mir alle Reports auflistet: 

def create_dataframe():
    columns = ['ReportID', 'created_by_pipe', 'connected_data', 'fig_name', 'df_name', 'author', 'ListOfUsers']
    df = pd.DataFrame(columns=columns)
    return df

def get_plot_title(fig):
    title = fig.layout.title.text if fig.layout.title.text else "No title found"
    return title

def add_data_to_dataframe(df, report):
    report_ids = report.ReportID
    created_by_pipe = report.created_by_pipe
    connected_data = "NN"
    fig_names = get_plot_title(report.fig) 
    df_names = "NN"
    authors = report.ListOfUsers[0]
    list_of_users = report.ListOfUsers

    # Füge die Daten in das DataFrame ein
    data_dict = {'ReportID': report_ids,
                 'created_by_pipe': created_by_pipe,
                 'connected_data': connected_data,
                 'fig_name': fig_names,
                 'df_name': df_names,
                 'author': authors,
                 'ListOfUsers': list_of_users}
    df = df.append(pd.DataFrame(data_dict))
    df.reset_index(drop=True, inplace=True)

    return df

def save_dataframe_as_pickle(df, filename):
    with open(filename, 'wb') as f:
        pickle.dump(df, f)
    print(f"Das DataFrame wurde als Pickle-Datei unter dem Namen '{filename}' gespeichert.")

def load_dataframe_from_pickle(filename):
    with open(filename, 'rb') as f:
        df = pickle.load(f)
    print(f"Das DataFrame wurde aus der Pickle-Datei '{filename}' geladen.")
    return df

def create_or_load_dataframe(report: Report) -> pd.DataFrame:
    if os.path.exists(current_app.config['DB_REPORTS']):
        df = load_dataframe_from_pickle(current_app.config['DB_REPORTS'])
        df = add_data_to_dataframe(df, report)
        save_dataframe_as_pickle(df, current_app.config['DB_REPORTS'])
    else:
        df = create_dataframe()
        df = add_data_to_dataframe(df, report)
        save_dataframe_as_pickle(df, current_app.config['DB_REPORTS'])
    return
    
