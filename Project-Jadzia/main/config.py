#!/bin python

from pathlib import Path
import os

curr_path = "/app/"

bash_msconvert = "sudo docker run -it --rm -e WINEDEBUG=-all -v /your/data:/data chambm/pwiz-skyline-i-agree-to-the-vendor-liscenses wine msconvert "
windows_msconvert = Path(r"C:\Users\Biotechnologie\KNIME\knime_3.3.2\plugins\de.openms.win32.x86_64_2.1.0.201704211842\payload\bin\pwiz-bin\msconvert.exe")
wrk_dir = "/home/labbikatz/ProjectJadzia/ProjectJadzia/Project-Jadzia" 
windows_wrk_dir = r"C:\Users\Biotechnologie\Documents\Bioinformatik\src\ProjectJadzia\Project-Jadzia"

class Config:
    SQLALCHEMY_DATABASE_URI = os.path.join('sqlite:///'+ curr_path, "db.sqlite3") 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WIFF_FOLDER = os.path.join(curr_path, "uploads", "wiff") 
    MZML_FOLDER = os.path.join(curr_path, "uploads", "mzml")
    PROCESS_FOLDER = os.path.join(curr_path, "uploads", "process")
    REPORT_FOLDER = os.path.join(curr_path, "uploads", "report")
    DATA_ANALYSES_CONFIG_FOLDER = os.path.join(curr_path, "uploads", "config", "data_analyses")
    ALLOWED_EXTENSIONS = ['wiff', 'scan', 'txt'] 
    ALLOWED_EXTENSIONS_HPLC = ['txt']
    CURR_PATH = curr_path
    DB_REPORTS = os.path.join(curr_path, "db_reports.pd")
    DB_PIPELINE = os.path.join(curr_path, "pipeline.json")
    DB_USERS = os.path.join(curr_path,"users.json" )
    HPLC_FOLDER = os.path.join(curr_path, "hplc")

