from sys import stdin

from SPARQLToSQL.translator import *
from SPARQLToSQL.mapping import load_yaml
from SPARQLToSQL.SparqlLexer import *
from SPARQLToSQL.sql_functions import *


def translate():
    load_yaml()

    sparql_query = stdin.readline()
    tree = parse_sparql_string(sparql_query)
    project_list = var_to_string(tree.selectQuery().var())
    group_graph_pattern = tree.selectQuery().whereClause().groupGraphPattern()

    # translation
    sqlObject = trans(group_graph_pattern)
    sqlObject = assign_pr_list(project_list, sqlObject)

    sql_query = sqlObject.build_sql()
    print(sql_query)

def parse_sparql_string(sparql_query):
    """
    :param sparql_query: text
    :return: SPARQL query object : Parser.SparqlParser.QueryContext
    """
    try:
        import sys, fileinput
        lexer = SparqlLexer(InputStream(sparql_query))
        stream = CommonTokenStream(lexer)
        parser = SparqlParser(stream)

        return parser.query()
    except RuntimeError:
        print("Parsing error.")
        raise

if __name__ == '__main__':
    translate()
