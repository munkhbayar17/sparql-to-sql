import sqlite3
import os

from SPARQLToSQL.constants import *


def init_sqlite(build_mode=False):
	global sql_path
	sql_path = ""

	if(build_mode):
		sql_path = "SPARQLToSQL/"

	# create persons
	print("Building dataset in sqlite ...")

	persons_conn_str = sql_path + "persons.db"
	capitals_conn_str = sql_path + "capitals.db"
	currencies_conn_str = sql_path + "currencies.db"

	global connPersons
	global connCurrencies
	global connCapitals

	if os.path.isfile(persons_conn_str):
		connPersons = create_connection(persons_conn_str)
	else:
		connPersons = create_connection(persons_conn_str)
		insert_persons(connPersons)

	if os.path.isfile(capitals_conn_str):
		connCapitals = create_connection(capitals_conn_str)
	else:
		connCapitals = create_connection(capitals_conn_str)
		load_from_rdf(connCapitals, "rdf/capitals.rdf")

	if os.path.isfile(currencies_conn_str):
		connCurrencies = create_connection(currencies_conn_str)
	else:
		connCurrencies = create_connection(currencies_conn_str)
		load_from_rdf(connCurrencies, "rdf/currencies.rdf")

	global current_connection
	current_connection = connPersons

	global current_db_name
	current_db_name = "Persons"

	print("Datasets created.")


def select_db(db_name):
	global current_connection
	if db_name == "Persons":
		current_connection = create_connection(sql_path + "persons.db")
	elif db_name == "Capitals":
		current_connection = create_connection(sql_path + "capitals.db")
	elif db_name == "Currencies":
		current_connection = create_connection(sql_path + "currencies.db")
	current_db_name = db_name


def create_connection(db_file):
	try:
		connection = sqlite3.connect(db_file)
		return connection

	except RuntimeError:
		print("Could initiate sqlite database!")
		raise

	return None


def create_table(connection, create_table_sql):
	try:
		cursor = connection.cursor()
		cursor.execute(create_table_sql)
	except RuntimeError as e:
		print(e)


def insert(conn, sub, pre, obj):
	try:
		cursor = conn.cursor()
		query = "INSERT INTO Triple(s, p, o) VALUES('{0}', '{1}', '{2}')".format(sub, pre, obj)
		cursor.execute(query)
		conn.commit()

	except sqlite3.OperationalError as e:
		print(e)
		raise


def insert_persons(conn):
	try:
		create_table_sql = open(sql_path + "sql/create_table.sql", "r")
		create_table(conn, create_table_sql.read())

		insert_sql = open(sql_path + "sql/persons.sql", "r").read()
		cursor = conn.cursor()
		cursor.executescript(insert_sql)
		print(insert_sql)

	except sqlite3.OperationalError as e:
		print(COLOR_FAIL + "\nPersons SQL script failed !\n" + COLOR_END)


def validate_query(select_sql):
	validQuery = False

	try:
		# if table is not created then create it
		create_table_sql = open(sql_path + "sql/create_table.sql", "r")
		create_table(current_connection, create_table_sql.read())

		cursor = current_connection.cursor()
		cursor.execute(select_sql)

		rows = cursor.fetchall()

		result_str = ""

		validQuery = True

	except sqlite3.OperationalError as e:
		print(COLOR_FAIL + "\nSQL select query is not valid !\n" + COLOR_END)

	return validQuery


def run_query(select_sql):
	try:
		# if table is not created then create it
		create_table_sql = open(sql_path + "sql/create_table.sql", "r")
		create_table(current_connection, create_table_sql.read())

		cursor = current_connection.cursor()
		cursor.execute(select_sql)

		return cursor.fetchall()

	except sqlite3.OperationalError as e:
		print(COLOR_FAIL + "\nSQL select query is not valid !\n" + COLOR_END)


def truncate():
	try:
		cursor = connPersons.cursor()
		cursor.execute("delete from Triple")
		connPersons.commit()

		cursor = connCapitals.cursor()
		cursor.execute("delete from Triple")
		connCapitals.commit()

		cursor = connCurrencies.cursor()
		cursor.execute("delete from Triple")
		connCurrencies.commit()

	except sqlite3.OperationalError as e:
		print(COLOR_FAIL + "\nTruncate failed !\n" + COLOR_END)

def load_from_rdf(conn, filename):
	try:
		create_table_sql = open(sql_path + "sql/create_table.sql", "r")
		create_table(conn, create_table_sql.read())

		from rdflib.graph import Graph
		g = Graph()
		g.parse(sql_path + filename, format="xml")

		for subject, predicate, obj in g:
			if (subject, predicate, obj) in g:
				print(subject, predicate, obj)
				insert(conn, subject, predicate, obj)
			else:
				print("RDF file {0} iteration error!".format(filename))

	except sqlite3.OperationalError as e:
		print(COLOR_FAIL + "\nRDF file {0} failed !\n".format(filename) + COLOR_END)


def fetch_predicates(db_name = None):
	try:
		cursor = current_connection.cursor()
		cursor.execute("select distinct p from Triple")

		predicates = [];
		rows = cursor.fetchall()

		for row in rows:
			predicates.append(row[0])

		return predicates

	except sqlite3.OperationalError as e:
		print(COLOR_FAIL + "\nSQL select query is not valid !\n" + COLOR_END)


def reload_datasets():
	truncate()
	insert_persons(connPersons)
	load_from_rdf(connCapitals, "rdf/capitals.rdf")
	load_from_rdf(connCurrencies, "rdf/currencies.rdf")
	return 1;

def get_db_name():
	return current_db_name