from antlr4.tree import Tree

from Classes.RDFClasses import *
from Classes.RelationalClasses import SQLProject


# translator helper

def is_variable(element):
	if isinstance(element, Variable):
		return Tree
	else:
		return False


def findCommonAttributes(tp1, tp2):
	attributes = []
	if (tp1.sp.context == tp2.sp.context):
		attributes.append(tp1.sp.context)
	if (tp1.pp.context == tp2.pp.context):
		attributes.append(tp1.pp.context)
	if (tp1.op.context == tp2.op.context):
		attributes.append(tp1.op.context)
	if (tp1.op.context == tp2.sp.context):
		attributes.append(tp1.op.context)
	if (tp1.sp.context == tp2.op.context):
		attributes.append(tp1.sp.context)
	return attributes


def findUncommonAttributes(tp1, tp2):
	uncommonAttrs = []
	commonAttrs = []

	uncommonAttrs = pushTripleToArray(tp1, uncommonAttrs)
	uncommonAttrs = pushTripleToArray(tp2, uncommonAttrs)

	if (tp1.sp.context == tp2.sp.context):
		commonAttrs.append(tp2.sp.context)
		uncommonAttrs.remove(tp2.sp.context)
	if (tp1.sp.context == tp2.pp.context):
		commonAttrs.append(tp2.pp.context)
		uncommonAttrs.remove(tp2.pp.context)
	if (tp1.sp.context == tp2.op.context):
		commonAttrs.append(tp1.op.context)
		uncommonAttrs.remove(tp2.op.context)
	if (tp1.pp.context == tp2.pp.context):
		commonAttrs.append(tp2.pp.context)
		uncommonAttrs.remove(tp2.pp.context)
	if (tp1.pp.context == tp2.op.context):
		commonAttrs.append(tp2.op.context)
		uncommonAttrs.remove(tp2.op)
	if (tp1.op.context == tp2.op.context):
		commonAttrs.append(tp2.op.context)
		uncommonAttrs.remove(tp2.op.context)
	return uncommonAttrs


# add triple elements to array
def pushTripleToArray(tp, narray):
	if arrayContains(tp.sp.context, narray) == False:
		narray.append(tp.sp.context)
	if arrayContains(tp.pp.context, narray) == False:
		narray.append(tp.pp.context)
	if arrayContains(tp.op.context, narray) == False:
		narray.append(tp.op.context)
		return narray


def arrayContains(node, array):
	if any(node in elem for elem in array):
		return True
	else:
		return False


# remove " and " on the beginning
def prSQLFormat(condSQL):
	if (len(condSQL) > 0):
		return condSQL[5:]
	else:
		return condSQL


def var_to_pr_list(projectList):
	pr_list = []
	for pr in projectList:
		pr_list.append(SQLProject(pr))

	return pr_list
