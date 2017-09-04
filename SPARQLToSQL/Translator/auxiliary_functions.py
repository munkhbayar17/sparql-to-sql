# auxiliary translation functions

def term(termName):
	termName = termName.replace("?", "")
	termName = termName.replace("$", "")
	return termName


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