import yaml

from SPARQLToSQL.Classes import Relation
from SPARQLToSQL.constants import *
from SPARQLToSQL.SparqlParser import TerminalNode


def load_yaml(test_mode=False):
	try:
		import sys
		schema = open("../conf/schema.yml", "r")

		schema_obj = yaml.load(schema)

		relation_name = schema_obj['relation']['name']
		relation_schema = schema_obj['relation']['schema']
		subject = schema_obj['relation']['subject']
		predicate = schema_obj['relation']['predicate']
		object = schema_obj['relation']['object']

		global RELATION
		RELATION = Relation(relation_name, relation_schema, subject, predicate, object)

	except RuntimeError:
		print("Could not load yaml file!")
		raise


def alpha(tp = None):
	return RELATION.full_name();


def beta(tp, pos):
	if pos == SUBJECT:
		return RELATION.subject

	if pos == PREDICATE:
		return RELATION.predicate

	if pos == OBJECT:
		return RELATION.object


def name(attr_name):
	attr_name = str(attr_name)

	return format_name(attr_name)


def format_name(attr_name):
	attr_name = attr_name.replace(':', '')
	attr_name = attr_name.replace('?', '')
	attr_name = attr_name.replace('$', '')
	attr_name = attr_name.replace('"', '')
	attr_name = attr_name.replace("'", '')

	return attr_name

def save_prologue(prologue):
	global BASE_PRE_VALUE
	BASE_PRE_VALUE = None

	global PREFIX_VAR
	PREFIX_VAR = None

	global PREFIX_VALUE
	PREFIX_VALUE = None

	if(prologue.baseDecl()):
		save_base_prefix(prologue.baseDecl())

	if(prologue.prefixDecl()):
		save_prefix(prologue.prefixDecl())

def save_base_prefix(baseDecl):
	global BASE_PRE_VALUE
	BASE_PRE_VALUE = getBaseDeclTerminalNode(baseDecl)
	print("BASE_PRE_VALUE: {0}".format(BASE_PRE_VALUE))

def save_prefix(prefixDecl):
	if isinstance(prefixDecl, list):
		prefixDecl = prefixDecl[0]

	# PREFIX
	if(prefixDecl.invokingState == 150
	   and len(prefixDecl.children) > 2):
		global PREFIX_VALUE
		PREFIX_VALUE = str(prefixDecl.children[2])

		global PREFIX_VAR
		PREFIX_VAR = str(prefixDecl.children[1]).split(':')[0]
		print("PREFIX_VAR: {0}".format(PREFIX_VAR))
		print("PREFIX_VALUE: {0}".format(PREFIX_VALUE))

def get_base_prefix():
	return BASE_PRE_VALUE

def get_prefix_var():
	return PREFIX_VAR

def get_prefix_value():
	return PREFIX_VALUE

def getBaseDeclTerminalNode(parent):
	if isinstance(parent, list):
		parent = parent[0]

	# BASE
	if(parent.invokingState == 147 and parent.children and len(parent.children) > 1):
		return str(parent.children[1])