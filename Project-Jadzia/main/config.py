#!/bin python

wrk_dir = "/home/labbikatz/ProjectJadzia/ProjectJadzia/Project-Jadzia" 

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = f"{wrk_dir}/uploads/wiff"
    ALLOWED_EXTENSIONS = ['wiff', 'scan', 'txt'] 

