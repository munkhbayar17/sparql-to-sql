import json

from flask import Flask
from flask import (render_template, request)

from Controller.controller import *
from Connection.sqlite import run_query, validate_query

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/trans', methods=['POST'])
def trans():
	request_json = request.get_json()
	sparql_query = request_json["sparql"]
	translator_type = request_json["translatorType"]
	return translate_for_ui(sparql_query, translator_type)


@app.route('/run', methods=['POST'])
def run():
	sql_query = request.data.decode("utf-8")
	return run_sql_for_ui(sql_query)

@app.route('/changedb', methods=['POST'])
def changedb():
	db_name = request.data.decode("utf-8")
	return change_dataset(db_name)
