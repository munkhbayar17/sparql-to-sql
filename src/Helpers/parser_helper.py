from antlr4.tree import Tree

from Classes.RDFClasses import *
from Parser.SparqlParser import *
from Translator.auxiliary_functions import *


# parser helper

def convert_from_triple_block(tripleBlock):
	if (isinstance(tripleBlock, list)):
		tripleBlock = tripleBlock[0]

	tripleSS = tripleBlock.triplesSameSubject()

	sub = get_subject(tripleSS.varOrTerm())
	pre = get_verb(tripleSS.propertyListNotEmpty().verb()[0])
	obj = get_object(tripleSS.propertyListNotEmpty().objectList()[0])

	return TriplePattern(sub, pre, obj)


def convert_triple_block(varOrTerm, verbCtx, objectCtx):
	sub = get_subject(varOrTerm)
	pre = get_verb(verbCtx)
	obj = get_object(objectCtx)

	return TriplePattern(sub, pre, obj)


def get_var(var):
	if term(str(var.VAR1())):
		return Variable(term(str(var.VAR1())))
	else:
		return Variable(term(str(var.VAR2())))


def get_IRI(iri):
	return IRI(str(iri.prefixedName().PNAME_LN()))


def get_literal(literal):
	stringLiteral = literal.rdfLiteral().string().STRING_LITERAL1()
	if stringLiteral is None:
		stringLiteral = literal.rdfLiteral().string().STRING_LITERAL2()
	return Literal(str(stringLiteral))


def getNumericLiteral(literal):
	if literal.numericLiteralUnsigned():
		return getNumericLiteralUnsigned(literal.numericLiteralUnsigned())
	elif literal.numericLiteralPositive():
		return getNumericLiteralPositive(literal.numericLiteralPositive())
	elif literal.numericLiteralNegative():
		return getNumericLiteralNegative(literal.numericLiteralNegative())


def getNumericLiteralUnsigned(literal):
	if literal.INTEGER():
		return literal.INTEGER()
	elif literal.DECIMAL():
		return literal.DECIMAL()
	elif literal.DOUBLE():
		return literal.DOUBLE()


def getNumericLiteralPositive(literal):
	if literal.INTEGER_POSITIVE():
		return literal.INTEGER_POSITIVE()
	elif literal.DECIMAL_POSITIVE():
		return literal.DECIMAL_POSITIVE()
	elif literal.DOUBLE_POSITIVE():
		return literal.DOUBLE_POSITIVE()


def getNumericLiteralNegative(literal):
	if literal.INTEGER_NEGATIVE():
		return literal.INTEGER_NEGATIVE()
	elif literal.DECIMAL_POSITIVE():
		return literal.DECIMAL_NEGATIVE()
	elif literal.DOUBLE_POSITIVE():
		return literal.DOUBLE_NEGATIVE()


def getBooleanLiteral(literal):
	return literal


def getTerminalNode(parent):
	for child in parent.getChildren():
		if isinstance(child, TerminalNode):
			return child


# get subject string when the subject is IVL
def get_subject(varOrTerm):
	if isinstance(varOrTerm, SparqlParser.VarOrTermContext):
		if (varOrTerm.var()):
			# node is Variable
			return get_var(varOrTerm.var())
		elif (varOrTerm.graphTerm()):
			graphTerm = varOrTerm.graphTerm()
			# if the node is GraphTerm (Literal or IRI)
			if (graphTerm.rdfLiteral()):
				# node is Literal
				return get_literal(graphTerm)
			elif (graphTerm.iriRef()):
				# node is IRI
				return get_IRI(graphTerm.iriRef())
	elif isinstance(varOrTerm, Tree.ErrorNodeImpl):
		return IRI(str(varOrTerm))


# get predicate string when the predicate is IV
def get_verb(verbContext):
	for node in verbContext.children:
		if isinstance(node, SparqlParser.VarOrIRIrefContext):
			if (node.var()):
				# verb has var
				return get_var(node.var())
			if (node.iriRef()):
				# verb has IRI
				return get_IRI(node.iriRef())


# get object string when the object is IVL
def get_object(objectListCtx):
	if (objectListCtx.object()):
		for objectCtx in objectListCtx.object():
			if (objectCtx.graphNode().varOrTerm()):
				return get_subject(objectCtx.graphNode().varOrTerm())


def var_to_string(varList):
	if isinstance(varList, list):
		strList = []
		for variable in varList:
			strList.append(get_var(variable).to_string())
		return strList
	else:
		return get_var(varList).to_string()
