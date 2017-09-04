from sys import stdin
import sys
sys.path.append("/sparql/src/")
from sparql.src.Parser import SparqlParser, SparqlLexer
from sparql.src.Translator.translator import *
from sparql.src.Translator.mapping import load_yaml
from sparql.src.Helpers.parser_helper import var_to_string


def translate():
    sparql_query = stdin.readline()
    tree = parse_sparql_string(sparql_query)
    project_list = var_to_string(tree.selectQuery().var())
    group_graph_pattern = tree.selectQuery().whereClause().groupGraphPattern()

    # translation
    sqlObject = trans(group_graph_pattern)
    sqlObject = assign_pr_list(project_list, sqlObject)

    sql_query = sqlObject.build_sql()
    print(sql_query)


if __name__ == '__main__':
    load_yaml()
