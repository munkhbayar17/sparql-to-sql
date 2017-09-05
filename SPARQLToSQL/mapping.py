import yaml

from SPARQLToSQL.Classes import Relation
from SPARQLToSQL.constants import *


def load_yaml(test_mode=False):
    global RELATION
    RELATION = Relation("Triple", "RDFStore", "s", "p", "o")


def alpha(tp=None):
    return RELATION.full_name();


def beta(tp, pos):
    if pos == SUBJECT:
        return RELATION.subject

    if pos == PREDICATE:
        return RELATION.predicate

    if pos == OBJECT:
        return RELATION.object
