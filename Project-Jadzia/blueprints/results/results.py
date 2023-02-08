#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request
from werkzeug.utils import secure_filename

results = Blueprint('results', __name__)