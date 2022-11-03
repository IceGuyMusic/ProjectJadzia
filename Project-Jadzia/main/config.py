#!/bin python

bash_msconvert = "sudo docker run -it --rm -e WINEDEBUG=-all -v /your/data:/data chambm/pwiz-skyline-i-agree-to-the-vendor-liscenses wine msconvert "
wrk_dir = "/home/labbikatz/ProjectJadzia/ProjectJadzia/Project-Jadzia" 

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = f"{wrk_dir}/uploads/wiff"
    MZML_FOLDER = f"{wrk_dir}/uploads/mzml"
    ALLOWED_EXTENSIONS = ['wiff', 'scan', 'txt'] 

