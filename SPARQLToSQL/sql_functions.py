from SPARQLToSQL.parser_helper import *
from SPARQLToSQL.translation_helper import *
from SPARQLToSQL.sql_helper import *
from SPARQLToSQL.mapping import *


# Simple SPARQL query translator

def construct_SQL_object(tp):
	pr_list = genPRSQL(tp)
	fromClause = SQLTable(alpha(tp))
	conditions = genCondSQL(tp)

	return SQLQuery(pr_list, fromClause, conditions)


# named same as in Chebotko's paper
def genPRSQL(tp):
	pr_list = []

	pr_list.append(SQLProject(beta(tp, SUBJECT), name(tp.sp)))

	if (tp.sp != tp.pp):
		pr_list.append(SQLProject(beta(tp, PREDICATE), name(tp.pp)))

	if (tp.sp != tp.op):
		pr_list.append(SQLProject(beta(tp, OBJECT), name(tp.op)))

	return pr_list


# named same as in Chebotko's paper
def genCondSQL(tp):
	condition_list = []

	if (is_variable(tp.sp) == False):
		condition_list.append(SQLCondition(beta(tp, SUBJECT), OP_EQUALS, tp.sp))
	if (is_variable(tp.pp) == False):
		condition_list.append(SQLCondition(beta(tp, PREDICATE), OP_EQUALS, tp.pp))
	if (is_variable(tp.op) == False):
		condition_list.append(SQLCondition(beta(tp, OBJECT), OP_EQUALS, tp.op))

	if (tp.sp == tp.op):
		condition_list.append(SQLCondition(beta(tp, SUBJECT), OP_EQUALS, beta(tp, OBJECT)))
	if (tp.sp == tp.pp):
		condition_list.append(SQLCondition(beta(tp, SUBJECT), OP_EQUALS, beta(tp, PREDICATE)))
	if (tp.pp == tp.op):
		condition_list.append(SQLCondition(beta(tp, PREDICATE), OP_EQUALS, beta(tp, OBJECT)))

	return condition_list


# /Simple SPARQL query translator

# INNER/LEFT JOIN translator

def merge_SQL_objects(sql_obj1, sql_obj2, join_type, trans_mode, is_union=False):
	if trans_mode == 3:
		if is_union == False:
			if join_type == SQL_INNER_JOIN:
				if isinstance(sql_obj1, SQLQuery) & isinstance(sql_obj2, SQLQuery):
					return pr_merge_SQL_objects(sql_obj1, sql_obj2)

	table1 = SQLTable(sql_obj1.build_sql(), "q1", True)
	table2 = SQLTable(sql_obj2.build_sql(), "q2", True)

	sql_obj1.set_alias("q1")
	sql_obj2.set_alias("q2")

	# pr list
	if is_union:
		pr_list = build_union_obj_pr(sql_obj1, sql_obj2)
	else:
		pr_list = build_join_pr(sql_obj1, sql_obj2, join_type, trans_mode)

	# conditions
	conditions = None

	if is_union == False:
		conditions = build_join_conditions(sql_obj1, sql_obj2, trans_mode)

	return SQLJoinQuery(pr_list, table1, join_type, table2, conditions)


# Builds projection list of the sql join object which is currently being built
def build_join_pr(sql_obj1, sql_obj2, join_type, trans_mode):
	pr_list = []

	common_fields = find_common_pr(sql_obj1, sql_obj2)

	for common_pr in common_fields:
		# in trans-s, if q1 has no left outer join then project only q1.field without coalesce
		if (trans_mode == 1 or join_type_of_sql_obj(sql_obj1, SQL_LEFT_OUTER_JOIN)):
			common_pr.set_coalesce(
				"Coalesce({0}.{1}, {2}.{1})".format(sql_obj1.alias, common_pr.get_attr_name(), sql_obj2.alias),
				common_pr.get_attr_name())
		else:
			common_pr.set_coalesce("{0}.{1}".format(sql_obj1.alias, common_pr.get_attr_name()),
			                       common_pr.get_attr_name())

		pr_list.append(common_pr)

	for project in sql_obj1.pr_list:
		if project not in pr_list:
			if in_pr_list(project, common_fields) is False:
				new_pr = SQLProject(project.field, project.alias)
				pr_list.append(new_pr)

	for project in sql_obj2.pr_list:
		if project not in pr_list:
			if in_pr_list(project, common_fields) is False:
				new_pr = SQLProject(project.field, project.alias)
				pr_list.append(new_pr)

	return pr_list


def build_union_obj_pr(sql_obj1, sql_obj2):
	pr_list = []

	common_fields = find_common_pr(sql_obj1, sql_obj2)

	for project in sql_obj1.pr_list:
		if (project not in pr_list):
			if in_pr_list(project, common_fields) is False:
				pr_list.append(project)

	for project in sql_obj2.pr_list:
		if (project not in pr_list):
			if in_pr_list(project, common_fields) is False:
				pr_list.append(project)

	for common_pr in common_fields:
		common_pr.set_table_alias(sql_obj1.alias)
		pr_list.append(common_pr)

	return pr_list


def build_join_conditions(sql_obj1, sql_obj2, trans_mode):
	condList = []

	common_fields = find_common_cond_attrs(sql_obj1, sql_obj2)

	for project in common_fields:
		# TODO might need copier to avoid internal link of objects
		project1 = SQLProject(project.field, project.alias)
		project1.set_table_alias(sql_obj1.alias)

		project2 = SQLProject(project.field, project.alias)
		project2.set_table_alias(sql_obj2.alias)

		condList.append(SQLJoinCondition(project1, OP_EQUALS, project2, (trans_mode != 1)))

	return condList


# /INNER JOIN translator

# UNION translator

def unite_SQL_objects(sql_obj1, sql_obj2, trans_mode):
	if trans_mode == 1:
		union_part1 = merge_SQL_objects(sql_obj1, sql_obj2, SQL_LEFT_OUTER_JOIN, 1, True)
		union_part2 = merge_SQL_objects(sql_obj2, sql_obj1, SQL_LEFT_OUTER_JOIN, 1, True)
	else:
		union_part1 = create_outer_query(sql_obj1)
		union_part2 = create_outer_query(sql_obj2)

	return SQLUnionQuery(union_part1, union_part2)


# /UNION translator



# SQL object functions
def assign_pr_list(project_list, sql_obj):
	"""
	assigns projection list given in original SPARQL query text
	:param project_list: projection list given in original SPARQL text
	:param sql_obj: SQL object translated by function trans
	:return: SPARQL query object : Classes.RelationalClasses.SQLQuery
	"""
	pr_list = []
	for alias in project_list:
		pr_checked = alias_in_pr_list(alias, sql_obj.pr_list)
		if pr_checked != False:
			pr_list.append(pr_checked)

	sql_obj.pr_list = pr_list

	if isinstance(sql_obj, SQLUnionQuery):
		new_pr_list = []
		for pr in pr_list:
			pr_checked = alias_in_pr_list(pr.alias, sql_obj.query1.pr_list)
			if (pr_checked):
				new_pr_list.append(pr)
		sql_obj.query1.pr_list = new_pr_list

		new_pr_list = []
		for pr in pr_list:
			pr_checked = alias_in_pr_list(pr.alias, sql_obj.query2.pr_list)
			if (pr_checked):
				new_pr_list.append(pr)
		sql_obj.query2.pr_list = new_pr_list

	return sql_obj


def add_order_expr(order_clause, sql_obj):
	if order_clause.orderCondition():
		sql_order_conds = translate_order_cond(order_clause.orderCondition(), [])
		sql_obj.set_order_fields(sql_order_conds)

	return sql_obj


def translate_order_cond(order_condition, order_list):
	if isinstance(order_condition, list):
		for order_cond in order_condition:
			order_list = translate_order_cond(order_cond, order_list)
		return order_list
	else:
		if order_condition.var():
			order_list.append(SQLOrderField(get_var(order_condition.var()).context))
			return order_list
		elif order_condition.brackettedExpression():
			if order_condition.brackettedExpression().expression():
				expr = order_condition.brackettedExpression().expression()
				if expr.conditionalOrExpression():
					if expr.conditionalOrExpression().conditionalAndExpression():
						expr = expr.conditionalOrExpression().conditionalAndExpression()[0]
						if expr.valueLogical():
							if expr.valueLogical()[0].relationalExpression():
								if expr.valueLogical()[0].relationalExpression().numericExpression():
									expr = expr.valueLogical()[0].relationalExpression().numericExpression()[0]
									if expr.additiveExpression():
										if expr.additiveExpression().multiplicativeExpression():
											if expr.additiveExpression().multiplicativeExpression()[0].unaryExpression():
												expr = expr.additiveExpression().multiplicativeExpression()[0].unaryExpression()[0]
												if expr.primaryExpression():
													if expr.primaryExpression().var():
														order_list.append(SQLOrderField(get_var(expr.primaryExpression().var()).context, getTerminalNode(order_condition) ))
														return order_list





def pr_list_to_str_list(pr_list):
	"""
	converts pr list to string list which is comfortable to be serialized to json
	:param projectList: SQLProject list
	:return: string list
	"""
	str_list = []
	for pr in pr_list:
		str_list.append(pr.alias)

	return str_list


def apply_db_field_to_filter_var(sql_cond, sql_obj):
	sql_cond.field1 = find_attr_for_filter(sql_obj.pr_list, sql_cond.field1)

	for logicalExpr in sql_cond.logical_exprs:
		logicalExpr.field1 = find_attr_for_filter(sql_obj.pr_list, logicalExpr.field1)

	return sql_cond


def add_condition_to_union_obj(union_obj, sql_cond):
	# TODO: SOLVE IT
	# if in_pr_list(sql_cond.field1, union_obj.query1.pr_list):
	#	union_obj.query1.add_where_condition(sql_cond)
	# if in_pr_list(sql_cond.field1, union_obj.query2.pr_list):
	#	union_obj.query2.add_where_condition(sql_cond)
	return union_obj


# builds sql object from another sql. dedicated for simplified union translator when schemas are same
def create_outer_query(sql_obj):
	table = SQLTable(sql_obj.build_sql(), 'u', True)
	sql_outer_query = SQLQuery(sql_obj.pr_list, table, [])
	return sql_outer_query


# /SQL object functions

# Extension functions
def pr_merge_SQL_objects(sql_query_obj_1, sql_query_obj_2):
	"""
	Builds multi-table query instead of inner joins
	:param sql_query_obj_1: SQLQuery
	:param sql_query_obj_2: SQLQuery
	:return: SQL query with multi tables
	"""
	if sql_query_obj_1.is_hyper_query() is True and sql_query_obj_2.is_hyper_query() is False:
		return ext_join_SQL_object_to_SQL_hyper(sql_query_obj_1, sql_query_obj_2)

	if sql_query_obj_2.is_hyper_query() is True and sql_query_obj_1.is_hyper_query() is False:
		return ext_join_SQL_object_to_SQL_hyper(sql_query_obj_2, sql_query_obj_1)

	if sql_query_obj_2.is_hyper_query() is True and sql_query_obj_1.is_hyper_query() is True:
		return None

	sql_query_obj_1.table.set_alias("t1")
	sql_query_obj_2.table.set_alias("t2")

	tables = [sql_query_obj_1.table, sql_query_obj_2.table]

	# pr list
	pr_list = ext_build_join_pr(sql_query_obj_1, sql_query_obj_2)

	# conditions
	join_conditions = ext_find_join_conditions(sql_query_obj_1, sql_query_obj_2)
	null_conditions = ext_build_not_null_conditions(sql_query_obj_1, sql_query_obj_2, join_conditions)
	where_conditions = ext_build_where_conditions(sql_query_obj_1, sql_query_obj_2)

	sql_obj = SQLQuery(pr_list, tables, where_conditions, join_conditions)
	sql_obj.set_null_conditions(null_conditions)

	return sql_obj


def ext_join_SQL_object_to_SQL_hyper(sql_query_hyper, sql_query_obj):
	"""
	Adds sql table and conditions to another SQL query with multiple tables
	:param sql_query_hyper: SQL Query with multiple tables
	:param sql_query_obj:   SQL Query with one table
	:return: SQLQuery with multiple tables
	"""
	new_table_alias = generate_table_alias(sql_query_hyper)
	sql_query_obj.table.set_alias(new_table_alias)

	sql_query_hyper.tables.append(sql_query_obj.table)

	# pr list
	diff_pr_list = find_diff_attrs(sql_query_hyper, sql_query_obj)

	# conditions
	join_conditions = ext_find_join_conditions(sql_query_hyper, sql_query_obj)
	for cond in join_conditions:
		sql_query_hyper.add_join_condition(cond)
		sql_query_hyper.add_null_condition(SQLCondition(cond.field2, OP_SQL_NOT, SQL_NULL))

	for cond in sql_query_obj.where_conditions:
		if isinstance(cond.field1, str):
			cond.field1 = SQLProject(cond.field1)
		cond.field1.set_table_alias(new_table_alias)
		sql_query_hyper.add_where_condition(cond)

	# pr list
	for project in diff_pr_list:
		project.set_table_alias(new_table_alias)
		sql_query_hyper.pr_list.append(project)

	return sql_query_hyper


def ext_find_join_conditions(sql_query_obj_1, sql_query_obj_2):
	condList = []

	common_fields = find_common_cond_attrs(sql_query_obj_1, sql_query_obj_2)

	# Conditions which were to be used on inner join connection
	for project in common_fields:
		project1 = SQLProject(project.field)
		if (sql_query_obj_1.is_hyper_query() is True):
			project1.set_table_alias(sql_query_obj_1.tables[0].alias)
		else:
			project1.set_table_alias(sql_query_obj_1.table.alias)

		project2 = SQLProject(project.field)
		if (sql_query_obj_2.is_hyper_query() is True):
			project2.set_table_alias(sql_query_obj_2.tables[0].alias)
		else:
			project2.set_table_alias(sql_query_obj_2.table.alias)

		condList.append(SQLCondition(project1, OP_EQUALS, project2))

	return condList


# used only when joining two sql queries each of which has only one table
def ext_build_not_null_conditions(sql_query_obj_1, sql_query_obj_2, condList):
	nullCondList = []

	# IS NOT NULL conditions for inner join connecting conditions
	# they could be added inside for loop above, but for the UX it is better to add after main connections
	cond_count = len(condList)

	for cond in condList:
		nullCondList.append(SQLCondition(cond.field1, OP_SQL_NOT, SQL_NULL))
		nullCondList.append(SQLCondition(cond.field2, OP_SQL_NOT, SQL_NULL))

	return nullCondList


def ext_build_where_conditions(sql_query_obj_1, sql_query_obj_2):
	condList = []

	for cond in sql_query_obj_1.where_conditions:
		if isinstance(cond.field1, SQLProject) is False:
			cond.field1 = SQLProject(str(cond.field1), sql_query_obj_1.table.alias)
		cond.field1.set_table_alias(sql_query_obj_1.table.alias)
		condList.append(cond)

	for cond in sql_query_obj_2.where_conditions:
		if isinstance(cond.field1, SQLProject) is False:
			cond.field1 = SQLProject(str(cond.field1))
		cond.field1.set_table_alias(sql_query_obj_2.table.alias)
		condList.append(cond)

	return condList


def ext_build_join_pr(sql_obj1, sql_obj2):
	pr_list = []

	common_fields = find_common_pr(sql_obj1, sql_obj2)

	for common_pr in common_fields:
		common_pr.set_table_alias(sql_obj1.table.alias)
		pr_list.append(common_pr)

	for project in sql_obj1.pr_list:
		if project not in pr_list:
			if in_pr_list(project, common_fields) is False:
				project.set_table_alias(sql_obj1.table.alias)
				pr_list.append(project)

	for project in sql_obj2.pr_list:
		if project not in pr_list:
			if in_pr_list(project, common_fields) is False:
				project.set_table_alias(sql_obj2.table.alias)
				pr_list.append(project)

	return pr_list

# /Extension functions