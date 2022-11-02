#!/bin python
from flask import Flask, Blueprint, current_app, redirect, url_for, render_template, session, flash, request

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template('base.html')


