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

from Connection.sqlite import init_sqlite
from Controller.controller import translate
from Translator.mapping import load_yaml


def init_translator():
	load_yaml()
	init_sqlite()


def init_server():
	from routing import app
	app.config['debug'] = True
	url = "http://127.0.0.1:9292"
	threading.Timer(0.5, lambda: webbrowser.open(url)).start()
	app.run(host='0.0.0.0', port=9292)


# def translateQuery():
# 	sql = translate('''SELECT ?a ?n ?p WHERE {{?a :name ?n} {{?a :phone ?p} UNION {?a :cell ?p}}}''')
# 	print(sql)


if __name__ == '__main__':
	init_translator()
	init_server()
	# translateQuery()