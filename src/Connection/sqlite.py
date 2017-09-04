import sqlite3
import os

from Translator.constants import *



def init_sqlite(test_mode=False):
	global sql_path
	global current_connection
	current_connection = None

	global connPersons
	global connCapitals
	global connCurrencies

	if test_mode == True:
		sql_path = "../src/Connection/"
	else:
		sql_path = "Connection/"

	# create persons
	print("Building dataset in sqlite ...")

	persons_conn_str = sql_path + "persons.db"
	capitals_conn_str = sql_path + "capitals.db"
	currencies_conn_str = sql_path + "currencies.db"

	if os.path.isfile(persons_conn_str):
		connPersons = create_connection(persons_conn_str)
	else:
		connPersons = create_connection(persons_conn_str)
		insert_persons(connPersons)

	if os.path.isfile(capitals_conn_str):
		connCapitals = create_connection(capitals_conn_str)
	else:
		connCapitals = create_connection(capitals_conn_str)
		insert_capitals(connCapitals)

	if os.path.isfile(currencies_conn_str):
		connCurrencies = create_connection(currencies_conn_str)
	else:
		connCurrencies = create_connection(currencies_conn_str)
		insert_currencies(connCurrencies)

	current_connection = connPersons

	print("Dataset created.")


def select_db(db_name):
	global current_connection
	if db_name == "Persons":
		current_connection = create_connection(sql_path + "persons.db")
	elif db_name == "Capitals":
		current_connection = create_connection(sql_path + "capitals.db")
	elif db_name == "Currencies":
		current_connection = create_connection(sql_path + "currencies.db")


def create_connection(db_file):
	try:
		connection = sqlite3.connect(db_file)
		return connection

	except RuntimeError:
		print("Could initiate sqlite db")
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
		#conn.commit()
		#conn.close()

		return cursor.fetchall()

	except sqlite3.OperationalError as e:
		print(COLOR_FAIL + "\nPersons SQL script failed !\n" + COLOR_END)


def insert_capitals(conn):
	create_table_sql = open(sql_path + "sql/create_table.sql", "r")
	create_table(conn, create_table_sql.read())

	insert(conn, ":user1", ":firstname", "John")
	insert(conn, ":user1", ":surname", "Simmons")
	insert(conn, ":user2", ":surname", "Kobe")
	insert(conn, ":user2", ":surname", "Bryant")
	insert(conn, ":user2", ":plays", ":sport1")
	insert(conn, ":user2", ":livesIn", ":location1")
	insert(conn, ":user2", ":bornIn", ":location2")
	# sport
	insert(conn, ":sport1", ":name", "Basketball")
	insert(conn, ":sport1", ":name", "Football")
	insert(conn, ":sport1", ":name", "Hockey")
	insert(conn, ":sport1", ":name", "Baseball")
	# locations
	insert(conn, ":location1", ":name", "Los Angeles")
	insert(conn, ":location2", ":name", "Philadelphia")
	insert(conn, ":location3", ":name", "Oakland")
	insert(conn, ":location4", ":name", "California")
	insert(conn, ":location5", ":name", "USA")
	insert(conn, ":location6", ":name", "North America")

	insert(conn, ":location1", ":location", "Los Angeles")
	insert(conn, ":location2", ":location", "Philadelphia")
	insert(conn, ":location3", ":location", "Oakland")
	insert(conn, ":location4", ":location", "California")
	insert(conn, ":location5", ":location", "USA")
	insert(conn, ":location6", ":location", "North America")

	insert(conn, ":location1", ":isLocatedIn", ":location4")
	insert(conn, ":location3", ":isLocatedIn", ":location4")
	insert(conn, ":location4", ":isLocatedIn", ":location5")
	insert(conn, ":location5", ":isLocatedIn", ":location6")


def insert_currencies(conn):
	try:
		create_table_sql = open(sql_path + "sql/create_table.sql", "r")
		create_table(conn, create_table_sql.read())

		insert_sql = open(sql_path + "sql/currencies.sql", "r").read()
		cursor = conn.cursor()
		cursor.executescript(insert_sql)
		#conn.commit()
		#conn.close()

		return cursor.fetchall()

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
