from Classes.RelationalClasses import *


# SQL class helpers

def find_common_pr(sql_obj1, sql_obj2):
	"""
	Find common attrs for project list
	:param sql_obj1:
	:param sql_obj2:
	:return:
	"""
	commonpr_list = []

	for project1 in sql_obj1.pr_list:
		for project2 in sql_obj2.pr_list:
			if project1.alias == project2.alias:
				commonpr_list.append(SQLProject(field=project1.field, alias=project1.alias))

	return commonpr_list


def in_pr_list(project, pr_list):
	for pr in pr_list:
		if pr.alias == project.alias:
			return True

	return False


def alias_in_pr_list(alias, pr_list):
	for pr in pr_list:
		if pr.alias == alias:
			return pr

	return False

# JOIN helpers

def find_common_cond_attrs(sql_obj1, sql_obj2):
	"""
	Find common attributes for SQL join condition
	:param sql_obj1:
	:param sql_obj2:
	:return:
	"""
	commonpr_list = []

	for project1 in sql_obj1.pr_list:
		for project2 in sql_obj2.pr_list:
			if project1.alias == project2.alias:
				commonpr_list.append(project1)

	return commonpr_list

def find_diff_attrs(sql_obj1, sql_obj2):
	"""
	Find different attributes in sql_obj2
	"""
	diff_pr_list = []

	for project1 in sql_obj2.pr_list:
		if project1 not in diff_pr_list and in_pr_list(project1, sql_obj1.pr_list) == False:
			diff_pr_list.append(project1)

	return diff_pr_list

def join_type_of_sql_obj(sql_obj, join_type):
	if isinstance(sql_obj, SQLJoinQuery):
		if sql_obj.join_type == join_type:
			return True

	return False

# /JOIN helpers

# FILTER helpers

def find_attr_for_filter(pr_list, field):
	for pr in pr_list:
		if pr.alias == str(field):
			new_pr = SQLProject(pr.field)
			if pr.has_table_alias() == True:
				new_pr.set_table_alias(pr.table_alias)
			return new_pr

	return field

# /FILTER helpers

def generate_table_alias(sql_query_obj):
	if sql_query_obj.is_hyper_query() is True:
		import re
		return "t{0}".format(int(re.search(r'\d+', sql_query_obj.tables[-1].alias).group())+1)
	else:
		return "t1"
