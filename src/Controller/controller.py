import json

from Connection.sqlite import run_query, validate_query, select_db
from Translator.translator import *
from Helpers.parser_helper import var_to_string


def translate(sparql_query, test_mode=False):
	"""
	translates an SPARQL query into corresponding SQL query and prints it if it is in test mode
	:param sparql_query: text
	:return: SQL query object: Classes.RelationalClasses.SQLQuery
	"""
	tree = parse_sparql_string(sparql_query)
	project_list = var_to_string(tree.selectQuery().var())
	group_graph_pattern = tree.selectQuery().whereClause().groupGraphPattern()

	# translation
	sqlObject = trans(group_graph_pattern)
	sqlObject = assign_pr_list(project_list, sqlObject)

	sql_query_string = sqlObject.build_sql()

	if test_mode == True:
		print(sql_query_string)
	else:
		return sql_query_string


# Translation functions for web interface
def translate_for_ui(sparql_query, translator_type):
	"""
	translates an SPARQL query into corresponding SQL query and provides sql query result
	:param sparql_query: text
	:return: SQL query object: Classes.RelationalClasses.SQLQuery, all rows
	"""
	tree = parse_sparql_string(sparql_query)
	projectList = var_to_string(tree.selectQuery().var())
	groupGraphPattern = tree.selectQuery().whereClause().groupGraphPattern()

	# Priyatna's extension translator
	if translator_type == '3':
		sql_object = trans(groupGraphPattern, 3)
	# Chebotko's simplified translator
	elif translator_type == '2':
		sql_object = trans(groupGraphPattern, 2)
	# Chebotko's original translator
	else:
		sql_object = trans(groupGraphPattern, 1)

	# project only variables in the original sparql query
	sql_object = assign_pr_list(projectList, sql_object)

	# parse order by expression
	if tree.selectQuery().solutionModifier():
		if tree.selectQuery().solutionModifier().orderClause():
			sql_object = add_order_expr(tree.selectQuery().solutionModifier().orderClause(), sql_object)

	sql_query_string = sql_object.build_sql()

	# is_valid = validate_query(sql_query_string)
    #
	# if is_valid:
	# 	query_result = run_query(sql_query_string)
	# 	sql_pr_list = pr_list_to_str_list(sql_object.pr_list)
	# else:
	# 	query_result = None
	# 	sql_pr_list = None

	return json.dumps({'sql': sql_query_string})#, 'is_valid': is_valid, 'header': sql_pr_list, 'result': query_result})


def run_sql_for_ui(sql_query_string):
	"""
	run SQL query and provides result
	:param sparqlQuery: text
	:return: query result
	"""

	is_valid = validate_query(sql_query_string)
	sql_pr_list = None
	query_result = None

	if is_valid:
		query_result = run_query(sql_query_string)

	return json.dumps({'sql': sql_query_string, 'is_valid': is_valid, 'header': sql_pr_list, 'result': query_result})


def change_dataset(db_name):
	"""
	Changes db according select box on the front-end
	:param db_name: db name
	"""
	if db_name:
		select_db(db_name)
		return json.dumps({'status': '1'})
	else:
		return json.dumps({'status': '0'})