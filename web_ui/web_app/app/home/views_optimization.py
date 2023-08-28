from flask import render_template, request, jsonify, Response, make_response, session, current_app, redirect, url_for,send_file
from zipfile import ZipFile
from . import home

@home.route('/optimization')
def optimization():
    return render_template('page/home/optimization.html')
    