class Relation:
	def __init__(self, nm, sc, sub, pre, obj):
		self.name = nm
		self.schema = sc
		self.subject = sub
		self.predicate = pre
		self.object = obj

	def to_string(self):
		return "Relation name:{0}\nsubject:{1}\npredicate:{2}\nobject:{3}".format(self.name, self.subject,
		                                                                          self.predicate, self.object)

	def full_name(self):
		if self.schema == None:
			return self.name
		else:
			return "{0}.{1}".format(self.schema, self.name)
