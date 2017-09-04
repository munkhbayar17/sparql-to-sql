from Classes.RDFClasses import IRI


class SQLQuery:
	def __init__(self, pr_list, tables, conditions, join_conditions=[]):
		self.pr_list = pr_list
		if isinstance(tables, list):
			self.tables = tables
		else:
			self.table = tables
			self.tables = []
			self.tables.append(tables)

		self.join_conditions = join_conditions
		self.where_conditions = conditions
		# conditions which are part of join conditions etc. table1.s is not null
		self.null_conditions = []
		# order by fields
		self.order_fields = []

	def __str__(self):
		return self.build_sql()

	# if the sql is to be joined with another sql through join other than inner join
	def set_join_type(self, joinType):
		self.joinType = joinType

	# if the sql is to be subquery for another sql
	def set_alias(self, alias):
		self.alias = alias

	# if the query has multi tables
	def is_hyper_query(self):
		if len(self.tables) > 1:
			return True
		else:
			return False

	def add_where_condition(self, sql_cond):
		self.where_conditions.append(sql_cond)

	def add_join_condition(self, sql_cond):
		self.join_conditions.append(sql_cond)

	def add_null_condition(self, sql_cond):
		self.null_conditions.append(sql_cond)

	# is not null conditions used in multi table query
	def set_null_conditions(self, conditions):
		self.null_conditions = conditions

	def set_order_fields(self, fields):
		self.order_fields = fields

	def add_order_field(self, field):
		self.order_fields.append(field)

	def build_sql(self):

		if self.is_hyper_query():
			return self.build_sql_hyper()

		if self.table.is_subquery == True:
			table_query = "({0}) as {1}".format(self.table.table_name, self.table.alias)
		else:
			if self.table.alias:
				table_query = "{0} {1}".format(self.table.table_name, self.table.alias)
			else:
				table_query = self.table

		SQL_string = "SELECT {0}\nFROM {1}".format(self.build_pr_clause(), table_query)

		if self.where_conditions is not None and len(self.where_conditions) > 0:
			SQL_string += "\nWHERE " + self.build_where_clause()

		if len(self.order_fields) > 0:
			SQL_string += self.build_order_by()

		return SQL_string

	def build_pr_clause(self):
		try:
			pr_clause = ""
			pr_clause = self.pr_list[0].pr_to_string()

			if len(self.pr_list) > 1:
				for pr in self.pr_list[1:]:
					pr_clause += ", {0}".format(pr.pr_to_string())

			return pr_clause

		except IndexError:
			print("SQL query has no project list to select")
			raise

	def build_where_clause(self):

		where_clause = ""

		for cond in self.where_conditions:

			if where_clause != "":
				where_clause += " AND "

			where_clause += sql_condition_to_string(cond)

		return where_clause

	def build_order_by(self):
		order_str = ""
		if len(self.order_fields) > 0:
			order_str += "\nORDER BY {0}".format(self.order_fields[0].to_string())
			if len(self.order_fields) > 1:
				for order_field in self.order_fields[1:]:
					order_str += ", {0}".format(order_field.to_string())

		return order_str

	def build_sql_hyper(self):

		tableQuery = "{0} {1}".format(self.tables[0].table_name, self.tables[0].alias)

		if len(self.tables) > 1:
			for table in self.tables[1:]:
				tableQuery += ", {0} {1}".format(table.table_name, table.alias)

		return "SELECT {0}\nFROM {1}\nWHERE {2}{3}".format(self.build_pr_clause_hyper(), tableQuery,
		                                                self.build_where_clause_hyper(), self.build_order_by())

	def build_pr_clause_hyper(self):
		try:
			pr_clause = ""
			pr_clause = self.pr_list[0].pr_to_with_table_alias()

			if len(self.pr_list) > 1:
				for pr in self.pr_list[1:]:
					pr_clause += ", {0}".format(pr.pr_to_with_table_alias())

			return pr_clause

		except IndexError:
			print("SQL query has no project list to select")
			raise

	def build_where_clause_hyper(self):

		where_clause = ""

		for cond in self.join_conditions:
			if where_clause != "":
				where_clause += " AND "
			where_clause += sql_condition_to_with_table_alias(cond)

		for cond in self.null_conditions:
			if where_clause != "":
				where_clause += " AND "
			where_clause += sql_condition_to_with_table_alias(cond)

		for cond in self.where_conditions:
			if where_clause != "":
				where_clause += " AND "
			where_clause += sql_condition_to_with_table_alias(cond)

		return where_clause


class SQLJoinQuery:
	def __init__(self, pr_list, table1, join_type, table2, conditions):
		self.pr_list = pr_list
		self.table1 = table1
		self.join_type = join_type
		self.table2 = table2
		self.join_conditions = conditions
		self.where_conditions = []
		self.order_fields = []

	def __str__(self):
		return self.build_sql()

	def set_join_type(self, joinType):
		self.join_type = joinType

	# if the sql is to be subquery for another sql
	def set_alias(self, alias):
		self.alias = alias

	def set_order_fields(self, fields):
		self.order_fields = fields

	def add_order_field(self, field):
		self.order_fields.append(field)

	def add_where_condition(self, sql_cond):
		self.where_conditions.append(sql_cond)

	def build_sql(self):
		queryFormat = ""

		if self.table1.is_subquery == True:
			queryFormat = "({0}) as {1}"
		else:
			queryFormat = "{0} as {1}"
		query1 = queryFormat.format(self.table1.table_name, self.table1.alias)

		if self.table2.is_subquery == True:
			queryFormat = "({0}) as {1}"
		else:
			queryFormat = "{0} as {1}"
		query2 = queryFormat.format(self.table2.table_name, self.table2.alias)

		# SELECT pr_list FROM table1 t1
		SQL_string = "SELECT {0}\nFROM {1}".format(self.pr_list_to_string(), query1)
		# JOIN table2 t2
		SQL_string += "\n{0} {1}".format(self.join_type, query2)
		# ON conditions
		SQL_string += "\nON {0}".format(self.join_conditions_to_string())
		# where conditions
		if len(self.where_conditions) > 0:
			SQL_string += "\n{0}".format(self.where_conditions_to_string())

		if len(self.order_fields) > 0:
			SQL_string += self.build_order_by()

		return SQL_string

	def pr_list_to_string(self):
		try:
			prClause = ""

			if hasattr(self.pr_list[0], 'table_alias'):
				prClause = "{0}.{1}".format(self.pr_list[0].table_alias, self.pr_list[0].get_attr_name())
			elif hasattr(self.pr_list[0], 'coalesce'):
				prClause = "{0} as {1}".format(self.pr_list[0].coalesce, self.pr_list[0].get_attr_name())
			else:
				prClause = self.pr_list[0].get_attr_name()

			if len(self.pr_list) > 1:
				for project in self.pr_list[1:]:
					if hasattr(project, 'table_alias'):
						prClause += ", {0}.{1}".format(project.table_alias, project.get_attr_name())
					elif hasattr(project, 'coalesce'):
						prClause += ", {0} as {1}".format(project.coalesce, project.get_attr_name())
					else:
						prClause += ", {0}".format(project.get_attr_name())

			return prClause

		except IndexError:
			print("SQL query has no project list to select")
			raise

	def join_conditions_to_string(self):

		if self.join_conditions is None or len(self.join_conditions) == 0:
			return "False"

		join_condition_string = str(self.join_conditions[0])

		if len(self.join_conditions) > 1:
			for join_condition in self.join_conditions[1:]:
				join_condition_string += " AND " + str(join_condition)

		return join_condition_string

	def where_conditions_to_string(self):

		if self.where_conditions is not None and len(self.where_conditions) > 0:
			condition_string = "WHERE " + sql_condition_to_string(self.where_conditions[0])

		if len(self.where_conditions) > 1:
			for where_condition in self.where_conditions[1:]:
				condition_string += " AND {0}".format(sql_condition_to_string(self.where_condition))

		return condition_string

	def build_order_by(self):
		order_str = ""
		if len(self.order_fields) > 0:
			order_str += "\nORDER BY {0}".format(self.order_fields[0].to_string())
			if len(self.order_fields) > 1:
				for order_field in self.order_fields[1:]:
					order_str += ", {0}".format(order_field.to_string())

		return order_str


class SQLUnionQuery:
	def __init__(self, query1, query2):
		self.query1 = query1
		self.query2 = query2
		self.pr_list = self.build_pr()

	def __str__(self):
		return self.build_sql()

	def set_alias(self, alias):
		self.alias = alias

	def set_join_type(self, joinType):
		self.join_type = joinType

	def build_pr(self):
		pr_list = []

		for pr in self.query1.pr_list:
			new_pr = SQLProject(pr.alias, pr.alias)
			if hasattr(pr, 'table_alias'):
				new_pr.set_table_alias(pr.table_alias)
			pr_list.append(new_pr)

		return pr_list

	def build_sql(self):
		SQL_string = "{0}\nUNION\n{1}".format(self.query1.build_sql(), self.query2.build_sql())

		return SQL_string


class SQLProject:
	def __init__(self, field, alias=None):
		self.field = field
		self.alias = alias

	def __str__(self):
		return self.get_attr_name()

	def has_table_alias(self):
		if hasattr(self, 'table_alias'):
			return True
		else:
			return False

	# subquery1.fieldName
	def set_table_alias(self, table_alias):
		self.table_alias = table_alias

	def set_alias(self, alias):
		self.alias = alias

	# function coalesce used on common attr between 2 tables/subqueries
	def set_coalesce(self, coalesceStr, alias):
		self.coalesce = coalesceStr
		self.alias = alias

	def get_attr_name(self):
		if self.alias == None:
			return self.field
		else:
			return self.alias

	def pr_to_string(self):
		if self.alias:
			return "{0} as {1}".format(self.field, self.alias)
		else:
			return self.field

	# designed for sqlHyperQuery
	def pr_to_with_table_alias(self):
		if hasattr(self, 'table_alias'):
			return "{0}.{1} as {2}".format(self.table_alias, self.field, self.alias)
		else:
			return "{0} as {1}".format(self.field, self.alias)


class SQLTable:
	def __init__(self, table, alias=None, is_subquery=False):
		self.table_name = table
		self.alias = alias
		self.is_subquery = is_subquery

	def set_alias(self, alias):
		self.alias = alias

	def __str__(self):
		if self.alias is None or len(self.alias) == 0:
			return self.table_name
		else:
			return "{0} {1}".format(self.table_name, self.alias)


class SQLCondition:
	def __init__(self, field1, operator, field2):
		self.field1 = field1
		self.field2 = field2
		self.operator = operator
		self.logical_exprs = []

	def __str__(self):
		return "({0}{1}{2})".format(self.get_attr_name1(), self.operator, self.get_attr_name2())

	def get_attr_name1(self):
		if self.field1.table_alias:
			return "{0}.{1}".format(self.field1.table_alias,
			                        self.field1.alias if self.field1.alias else self.field1.field)
		else:
			return "{0}".format(self.field1.alias if self.field1.alias else self.field1.field)

	def get_attr_name2(self):
		if self.field2.table_alias:
			return "{0}.{1}".format(self.field2.table_alias,
			                        self.field2.alias if self.field2.alias else self.field2.field)
		else:
			return "{0}".format(self.field2.alias if self.field2.alias else self.field2.field)

	def add_logical_expr(self, expr):
		self.logical_exprs.append(expr)

	def set_logical_connective(self, logical_con):
		self.logical_connective = logical_con


class SQLJoinCondition:
	def __init__(self, field1, operator, field2, simplified=False):
		self.field1 = field1
		self.field2 = field2
		self.operator = operator
		self.is_simplified = simplified

	def __str__(self):
		if self.is_simplified == False:
			condStr = "({0}{1}{2}".format(self.get_attr_name1(), self.operator, self.get_attr_name2())
			condStr += " or {0}=Null".format(self.get_attr_name1())
			condStr += " or {0}=Null)".format(self.get_attr_name2())
		else:
			condStr = "{0}{1}{2}".format(self.get_attr_name1(), self.operator, self.get_attr_name2())

		return condStr

	def get_attr_name1(self):
		if self.field1.table_alias:
			return "{0}.{1}".format(self.field1.table_alias,
			                        self.field1.alias if self.field1.alias else self.field1.field)
		else:
			return "{0}".format(self.field1.alias if self.field1.alias else self.field1.field)

	def get_attr_name2(self):
		if self.field2.table_alias:
			return "{0}.{1}".format(self.field2.table_alias,
			                        self.field2.alias if self.field2.alias else self.field2.field)
		else:
			return "{0}".format(self.field2.alias if self.field2.alias else self.field2.field)

	def is_simplified(self):
		if hasattr(self, 'simplify'):
			return self.simplify
		else:
			return False


class SQLOrderField:
	def __init__(self, field, func = None):
		self.field = field
		self.function = func

	def __str__(self):
		if self.function is None:
			return self.field
		else:
			return "{0} {1}".format(self.field, self.function)

	def to_string(self):
		if self.function is None:
			return self.field
		else:
			return "{0} {1}".format(self.field, self.function)

def sql_condition_to_string(cond):
	# if the field is RDF term quote is added
	if isinstance(cond.field1, IRI):
		condField1 = "'{0}'".format(cond.field1)
	else:
		condField1 = cond.field1

	if isinstance(cond.field2, IRI):
		condField2 = "'{0}'".format(cond.field2)
	else:
		condField2 = cond.field2

	condString = "{0} {1} {2}".format(condField1, cond.operator, condField2)

	# if there are logical conditions
	if len(cond.logical_exprs) > 0:
		for logicalCond in cond.logical_exprs:
			condString += " {0} {1}".format(logicalCond.logical_connective, sql_condition_to_string(logicalCond))
		condString = "( {0} )".format(condString)

	return condString


def sql_condition_to_with_table_alias(cond):
	# if the field is RDF term quote is added
	if isinstance(cond.field1, SQLProject):
		condField1 = "{0}.{1}".format(cond.field1.table_alias, cond.field1.field)
	elif isinstance(cond.field1, IRI):
		condField1 = "'{0}'".format(cond.field1)
	else:
		condField1 = cond.field1

	if isinstance(cond.field2, SQLProject):
		condField2 = "{0}.{1}".format(cond.field2.table_alias, cond.field2.field)
	elif isinstance(cond.field2, IRI):
		condField2 = "'{0}'".format(cond.field2)
	else:
		condField2 = cond.field2

	condString = "{0} {1} {2}".format(condField1, cond.operator, condField2)

	# if there are logical conditions
	if len(cond.logical_exprs) > 0:
		for logicalCond in cond.logical_exprs:
			condString += " {0} {1}".format(logicalCond.logical_connective,
			                                sql_condition_to_with_table_alias(logicalCond))
		condString = "( {0} )".format(condString)

	return condString
