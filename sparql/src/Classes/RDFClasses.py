# !begin - translator classes

# (IB)x(I)x(IBL)
class Triple:
	def __init__(self, sub, pre, obj):
		self.subject = sub
		self.predicate = pre
		self.object = obj

	def toString(self):
		return "{s:{0}, p:{1}, o:{2}}".format(self.subject, self.predicate, self.object)


# (IVL)x(IV)x(IVL)
class TriplePattern:
	def __init__(self, sub, pre, obj):
		# IVL
		self.sp = sub
		# IV
		self.pp = pre
		# IVL
		self.op = obj

	def toString(self):
		return "s:{0}, p:{1}, o:{2}".format(self.sp, self.pp, self.op)


#
class GraphPattern:
	def __init__(self, g1, op, g2):
		self.gp1 = g1
		self.operator = op
		self.gp2 = g2

	def allVariables():
		return []

	def toString(self):
		return "gp1: {0}\nop: {1}\ngp2: {2}".format(self.gp1.to_string(), self.operator, self.gp2.to_string())


# !end - translator classes

# !begin - RDF terms

class Variable:
	def __init__(self, con):
		self.context = con

	def __str__(self):
		return self.context

	def __repr__(self):
		return self.context

	def to_string(self):
		return self.context


class IRI:
	def __init__(self, con):
		self.context = con

	def __str__(self):
		return self.context


class Literal:
	def __init__(self, con):
		self.context = con

	def __str__(self):
		return self.context


class Blank:
	def __init__(self, con):
		self.context = con

	def __str__(self):
		return self.context

	def __repr__(self):
		return self.context

	def toString(self):
		return self.context

	# !end - RDF terms
