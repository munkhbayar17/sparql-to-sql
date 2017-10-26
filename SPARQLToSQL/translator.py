from sys import stdin
from SPARQLToSQL.mapping import load_yaml, save_base_prefix
from SPARQLToSQL.SparqlLexer import *
from SPARQLToSQL.sql_functions import *
from SPARQLToSQL.parser_helper import *
from SPARQLToSQL.sql_functions import *

def trans(pattern, trans_mode = 1):
	"""
	:param pattern: GroupGraphPatternContext|TriplesBlockContext
	:param trans_mode: # 1 = Original, 2 = Simplified, 3 = Extension
	:return: SPARQL query object : Classes.RelationalClasses.SQLJoinQuery|SQLQuery
	"""

	if(isinstance(pattern, SparqlParser.QueryContext)):
		save_prologue(pattern.prologue())
		pattern = pattern.selectQuery().whereClause().groupGraphPattern()

	sql_object = None

	if isinstance(pattern, list):
		sql_object = trans_multi_objects(pattern, trans_mode)

	# recursive control section
	if isinstance(pattern, SparqlParser.GroupGraphPatternContext):

		# grGP has Triple BLock
		if (pattern.tripleSameSubjecttriplesBlock()):

			# grGP has graphPatternNotTriples
			if (pattern.graphPatternNotTriples()):

				sql_object = trans_tri_block_and_group_gp(pattern, trans_mode)

			# grGP has only Triple Block(s)
			else:
				sql_object = trans(pattern.tripleSameSubjecttriplesBlock(), trans_mode)

		# grGP has only graphPatternNotTriples
		elif (pattern.graphPatternNotTriples()):

			sql_object = trans_gp_not_tri(pattern.graphPatternNotTriples(), trans_mode)

		if (pattern.filter()):
			# selectQuery has Filter expr
			sql_object = trans_filter(sql_object, pattern.filter())

	# TripleBlock translator
	elif isinstance(pattern, SparqlParser.TriplesBlockContext):
		sql_object = trans_tri_block(pattern, trans_mode)

	return sql_object


# Triple Block
def trans_tri_block(tripleBlock, trans_mode):
	"""
	:param tripleBlock: TripleBlockContext
	:return: SPARQL query object : Classes.RelationalClasses.SQLQuery
	"""
	verbList = tripleBlock.triplesSameSubject().propertyListNotEmpty().verb()
	objectList = tripleBlock.triplesSameSubject().propertyListNotEmpty().objectList()

	# if TripleBlock is single triple pattern
	if (len(verbList) == 1 and len(objectList) == 1):

		triplePattern1 = convert_from_triple_block(tripleBlock)
		sql_obj1 = construct_SQL_object(triplePattern1)

		# if TripleBlock has another TripleBlock inside it
		if (tripleBlock.triplesBlock()):
			sql_obj2 = trans_tri_block(tripleBlock.triplesBlock(), trans_mode)
			return merge_SQL_objects(sql_obj1, sql_obj2, SQL_INNER_JOIN, trans_mode)

		else:
			return sql_obj1

	# if tripleBlock has multiple triple patterns
	elif (len(verbList) == len(objectList)):
		return trans_multi_obj_tri_block(tripleBlock, trans_mode)


# Triple Block with multi objects
def trans_multi_obj_tri_block(tripleBlock, trans_mode):
	"""
	Translates a triple block which has multiple predicate-objects
	:param tripleBlock: TripleBlockContext
	:return: SPARQL query object : Classes.RelationalClasses.SQLJoinQuery
	"""
	verbList = tripleBlock.triplesSameSubject().propertyListNotEmpty().verb()
	objectList = tripleBlock.triplesSameSubject().propertyListNotEmpty().objectList()

	triplePattern1 = convert_from_triple_block(tripleBlock)
	sqlObj1 = construct_SQL_object(triplePattern1)

	for i in range(1, len(verbList)):
		triplePattern2 = convert_triple_block(tripleBlock.triplesSameSubject().varOrTerm(), verbList[i], objectList[i])
		sqlObj2 = construct_SQL_object(triplePattern2)

		sqlObj1 = merge_SQL_objects(sqlObj1, sqlObj2, SQL_INNER_JOIN, trans_mode)

	return sqlObj1


# Triple Block and GraphNotTriples
def trans_tri_block_and_group_gp(groupGraphPattern, trans_mode):
	"""
	Translates triple Block and graph pattern not triples and joins them
	:param groupGraphPattern:
	:return: SPARQL query object : Classes.RelationalClasses.SQLJoinQuery
	"""
	tripleBlock = groupGraphPattern.tripleSameSubjecttriplesBlock()
	graphPatternNotTriples = groupGraphPattern.graphPatternNotTriples()

	# first translate TripleBlock
	tripleBlockSQLObj = trans(tripleBlock, trans_mode)
	joinSQLObj = tripleBlockSQLObj

	if isinstance(graphPatternNotTriples, list):
		for graphPatternNotTriple in graphPatternNotTriples:
			gpNotTriSQLObj = trans_gp_not_tri(graphPatternNotTriple, trans_mode)

			joinType = SQL_INNER_JOIN

			if hasattr(gpNotTriSQLObj, 'joinType'):
				joinType = SQL_LEFT_OUTER_JOIN

			joinSQLObj = merge_SQL_objects(joinSQLObj, gpNotTriSQLObj, joinType, trans_mode)

		return joinSQLObj

	else:
		gpNotTriSQLObj = trans_gp_not_tri(graphPatternNotTriples, trans_mode)

		joinType = SQL_INNER_JOIN

		if gpNotTriSQLObj.joinType:
			joinType = SQL_LEFT_OUTER_JOIN

		return merge_SQL_objects(tripleBlockSQLObj, gpNotTriSQLObj, joinType, trans_mode)


# GraphPatternNotTriples
def trans_gp_not_tri(graphPatternNotTriples, trans_mode):
	"""
	Translates GraphPatternNotTriples

	:param graphPatternNotTriples:
	:return: SPARQL query object : Classes.RelationalClasses.SQLJoinQuery
	"""
	# if graphPatternNotTriples is list
	if isinstance(graphPatternNotTriples, list):
		joinSQLObj = trans_gp_not_tri(graphPatternNotTriples[0], trans_mode)

		if len(graphPatternNotTriples) > 1:
			for graphPatternNotTriple in graphPatternNotTriples[1:]:
				gpNotTriSQLObj = trans_gp_not_tri(graphPatternNotTriple, trans_mode)

				joinType = SQL_INNER_JOIN

				if hasattr(gpNotTriSQLObj, 'joinType'):
					joinType = SQL_LEFT_OUTER_JOIN

				joinSQLObj = merge_SQL_objects(joinSQLObj, gpNotTriSQLObj, joinType, trans_mode)

		return joinSQLObj

	# graphPatternNotTriples is single graph
	else:
		# OPTIONAL Graph Pattern
		if graphPatternNotTriples.optionalGraphPattern():
			sqlObj = trans(graphPatternNotTriples.optionalGraphPattern().groupGraphPattern(), trans_mode)
			sqlObj.set_join_type(SQL_LEFT_OUTER_JOIN)
			return sqlObj

		elif graphPatternNotTriples.groupOrUnionGraphPattern():
			return trans(graphPatternNotTriples.groupOrUnionGraphPattern().groupGraphPattern(), trans_mode)

		elif graphPatternNotTriples.graphGraphPattern():
			return graphPatternNotTriples.graphGraphPattern()


# UNION patterns
def trans_multi_objects(objects, trans_mode):
	"""
	translates groupGraphPatterns into SQL UNION query or Triple Blocks into SQL Join query
	:param objects:
	:return: SPARQL query object : Classes.RelationalClasses.SQLUnionQuery
	"""
	joined_sql_obj = trans(objects[0], trans_mode)

	if len(objects) > 1:
		for obj in objects[1:]:
			sqlObj = trans(obj, trans_mode)
			# if object is GroupGraphPattern then translate to SQL Union
			if isinstance(obj, SparqlParser.GroupGraphPatternContext):
				joined_sql_obj = unite_SQL_objects(joined_sql_obj, sqlObj, trans_mode)
			# if object is not GroupGraphPattern then translate to SQL Join
			else:
				joined_sql_obj = merge_SQL_objects(sqlObj, joined_sql_obj, SQL_INNER_JOIN, trans_mode)

	return joined_sql_obj


# /end of tran functions

# Filter translators


def trans_filter(sql_obj, filter_context):
	for filter in filter_context:
		sql_obj = translate_filter(sql_obj, filter.constraint())

	return sql_obj


def translate_filter(sql_obj, filter):
	if filter.brackettedExpression():
		sql_cond = translate_bracket_expr(filter.brackettedExpression())

		# if sql object is simple sql query,
		# then var in filter expr must be replaced with relational table field
		if isinstance(sql_obj, SQLQuery):
			sql_cond = apply_db_field_to_filter_var(sql_cond, sql_obj)

		if isinstance(sql_obj, SQLUnionQuery):
			sql_obj = add_condition_to_union_obj(sql_obj, sql_cond)
		else:
			sql_obj.add_where_condition(sql_cond)

	return sql_obj


def translate_bracket_expr(bracket):
	if bracket.expression():
		if bracket.expression().conditionalOrExpression():
			if bracket.expression().conditionalOrExpression().conditionalAndExpression():
				sql_cond = translate_cond_expr(
					bracket.expression().conditionalOrExpression().conditionalAndExpression())
				return sql_cond


def translate_cond_expr(condsAndExpr):
	sql_condition = None
	for condAndExpr in condsAndExpr:
		logical_connective = OP_SQL_OR
		if condAndExpr.valueLogical():
			for valueLogical in condAndExpr.valueLogical():
				if (len(condAndExpr.valueLogical()) > 1):
					logical_connective = OP_SQL_AND
				if valueLogical.relationalExpression():
					if sql_condition is None:
						sql_condition = translate_rel_expr(valueLogical.relationalExpression())
					else:
						logicalCond = translate_rel_expr(valueLogical.relationalExpression())
						logicalCond.set_logical_connective(logical_connective)
						sql_condition.add_logical_expr(logicalCond)
	return sql_condition


def translate_rel_expr(relationalExpr):
	if relationalExpr.numericExpression():
		# if the condition is numeric
		if len(relationalExpr.numericExpression()) == 2:
			field1 = translate_num_expr(relationalExpr.numericExpression()[0])
			field2 = translate_num_expr(relationalExpr.numericExpression()[1])
			operator = getTerminalNode(relationalExpr)
			return SQLCondition(field1, operator, field2)
		elif len(relationalExpr.numericExpression()) == 1:
			return translate_num_expr(relationalExpr.numericExpression()[0])


def translate_num_expr(numericExpr):
	if numericExpr.additiveExpression():
		if numericExpr.additiveExpression().multiplicativeExpression():
			if numericExpr.additiveExpression().multiplicativeExpression():
				return translate_multi_expr(numericExpr.additiveExpression().multiplicativeExpression())


def translate_multi_expr(multiExprs):
	for multiExpr in multiExprs:
		if multiExpr.unaryExpression():
			for unaryExpr in multiExpr.unaryExpression():
				return translate_primary_expr(unaryExpr.primaryExpression())


def translate_primary_expr(primaryExpr):
	# numeric expressions, ?x > 0, ?x = 0 ...
	if primaryExpr.var():
		return get_var(primaryExpr.var())
	elif primaryExpr.rdfLiteral():
		return get_literal(primaryExpr)
	elif primaryExpr.iriRefOrFunction():
		if primaryExpr.iriRefOrFunction.iriRef():
			return get_IRI(primaryExpr.iriRefOrFunction().iriRef())
	elif primaryExpr.numericLiteral():
		return getNumericLiteral(primaryExpr.numericLiteral())
	elif primaryExpr.booleanLiteral():
		return getBooleanLiteral(primaryExpr.booleanLiteral())
	# build in functions, BOUND(?x) ...
	elif primaryExpr.builtInCall():
		#TODO: if more functions other than bound is to be added,
		#it should be changed
		builtInFunction = getTerminalNode(primaryExpr.builtInCall())
		variable = get_var(primaryExpr.builtInCall().var())
		return SQLCondition(variable, OP_SQL_NOT, "null")


# /Filter translators

# Parser
def parse_sparql_string(sparql_query):
	"""
	:param sparql_query: text
	:return: SPARQL query object : Parser.SparqlParser.QueryContext
	"""
	try:
		lexer = SparqlLexer(InputStream(sparql_query))
		stream = CommonTokenStream(lexer)
		parser = SparqlParser(stream)

		return parser.query()
	except ErrorNode:
		print("Parsing error.")
		raise