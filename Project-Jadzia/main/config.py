#!/bin python

from pathlib import Path

bash_msconvert = "sudo docker run -it --rm -e WINEDEBUG=-all -v /your/data:/data chambm/pwiz-skyline-i-agree-to-the-vendor-liscenses wine msconvert "
windows_msconvert = Path(r"C:\Users\Biotechnologie\KNIME\knime_3.3.2\plugins\de.openms.win32.x86_64_2.1.0.201704211842\payload\bin\pwiz-bin\msconvert.exe")
wrk_dir = "/home/labbikatz/ProjectJadzia/ProjectJadzia/Project-Jadzia" 
windows_wrk_dir = r"C:\Users\Biotechnologie\Documents\Bioinformatik\src\ProjectJadzia\Project-Jadzia"

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = f"{wrk_dir}/uploads/wiff"
    MZML_FOLDER = f"{wrk_dir}/uploads/mzml"
    ALLOWED_EXTENSIONS = ['wiff', 'scan', 'txt'] 
    WIN_MZML_FOLDER = windows_wrk_dir + r"\uploads\mzml"
    WIN_UPLOAD_FOLDER = windows_wrk_dir + r"\uploads\wiff"
