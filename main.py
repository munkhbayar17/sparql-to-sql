"""
@author: Munkhbayar Nergui
@email: munkhbayar.nergui@postgrad.manchester.ac.uk
@org: 	University of Manchester
@Year: 	2017
@Place: Manchester, UK
@Desc:	SPARQL to SQL translation program
@Reference: Based on Artem Chebotko's approach
@Reference:
@Database schema: Vertical
"""

import threading, webbrowser

from SPARQLToSQL.sqlite import init_sqlite
from SPARQLToSQL.controller import translate
from SPARQLToSQL.mapping import load_yaml


def init_translator():
	load_yaml()
	init_sqlite(True)


def init_server():
	from SPARQLToSQL.routing import app
	app.config['debug'] = True
	url = "http://127.0.0.1:9292"
	threading.Timer(1, lambda: webbrowser.open(url)).start()
	app.run(host='0.0.0.0', port=9292)


if __name__ == '__main__':
	init_translator()
	init_server()