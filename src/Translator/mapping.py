import yaml

from Classes.Classes import Relation
from Translator.constants import *


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
