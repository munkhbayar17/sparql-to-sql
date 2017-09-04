from Connection.sqlite import init_sqlite
from Controller.controller import translate
from Translator.mapping import load_yaml


class SystemTest():
	def unionTest(self):
		""">>> translate('''SELECT ?book ?x ?y WHERE { { ?book dc10:title ?x } UNION { ?book dc11:title ?y } }''', True)
SELECT q1.book, x, y\nFROM (SELECT s as book, p as dc10title, o as x\nFROM Triple\nWHERE p = 'dc10:title') as q1\nLEFT OUTER JOIN (SELECT s as book, p as dc11title, o as y\nFROM Triple\nWHERE p = 'dc11:title') as q2\nON False\nUNION\nSELECT q1.book, x, y\nFROM (SELECT s as book, p as dc11title, o as y\nFROM Triple\nWHERE p = 'dc11:title') as q1\nLEFT OUTER JOIN (SELECT s as book, p as dc10title, o as x\nFROM Triple\nWHERE p = 'dc10:title') as q2\nON False"""

	def andTest(self):
		""">>> translate('''SELECT ?book ?x ?y WHERE { { ?book dc10:title ?x } { ?book dc11:title ?y } }''', True)
SELECT Coalesce(q1.book, q2.book) as book, x, y\nFROM (SELECT s as book, p as dc10title, o as x\nFROM Triple\nWHERE p = 'dc10:title') as q1\nINNER JOIN (SELECT s as book, p as dc11title, o as y\nFROM Triple\nWHERE p = 'dc11:title') as q2\nON (q1.book=q2.book or q1.book=Null or q2.book=Null)"""

	def andTest2(self):
		""">>> translate('''SELECT ?x ?y ?nickY WHERE { ?x foaf:knows ?y { ?y foaf:nick ?nickY } }''', True)
SELECT x, Coalesce(q1.y, q2.y) as y, nickY\nFROM (SELECT s as x, p as foafknows, o as y\nFROM Triple\nWHERE p = 'foaf:knows') as q1\nINNER JOIN (SELECT s as y, p as foafnick, o as nickY\nFROM Triple\nWHERE p = 'foaf:nick') as q2\nON (q1.y=q2.y or q1.y=Null or q2.y=Null)"""

	def optTest(self):
		""">>> translate('''SELECT ?x ?y ?nickY WHERE { {?x foaf:knows ?y} OPTIONAL { ?y foaf:nick ?nickY } }''', True)
SELECT x, Coalesce(q1.y, q2.y) as y, nickY\nFROM (SELECT s as x, p as foafknows, o as y\nFROM Triple\nWHERE p = 'foaf:knows') as q1\nLEFT OUTER JOIN (SELECT s as y, p as foafnick, o as nickY\nFROM Triple\nWHERE p = 'foaf:nick') as q2\nON (q1.y=q2.y or q1.y=Null or q2.y=Null)"""

	def optTest2(self):
		""">>> translate('''SELECT ?x ?y ?nickY WHERE { {?x foaf:knows ?y} OPTIONAL { ?y foaf:nick ?nickY OPTIONAL { ?y foaf:birthday ?bday } } }''', True)
SELECT x, Coalesce(q1.y, q2.y) as y, nickY\nFROM (SELECT s as x, p as foafknows, o as y\nFROM Triple\nWHERE p = 'foaf:knows') as q1\nINNER JOIN (SELECT Coalesce(q1.y, q2.y) as y, foafnick, nickY, foafbirthday, bday\nFROM (SELECT s as y, p as foafnick, o as nickY\nFROM Triple\nWHERE p = 'foaf:nick') as q1\nLEFT OUTER JOIN (SELECT s as y, p as foafbirthday, o as bday\nFROM Triple\nWHERE p = 'foaf:birthday') as q2\nON (q1.y=q2.y or q1.y=Null or q2.y=Null)) as q2\nON (q1.y=q2.y or q1.y=Null or q2.y=Null)"""

	def doubleOptTest(self):
		""">>> translate('''SELECT ?name ?mbox ?hpage WHERE { ?x foaf:name ?name . OPTIONAL { ?x foaf:mbox ?mbox } .OPTIONAL { ?x foaf:homepage ?hpage } }''', True)
SELECT name, mbox, hpage\nFROM (SELECT Coalesce(q1.x, q2.x) as x, foafname, name, foafmbox, mbox\nFROM (SELECT s as x, p as foafname, o as name\nFROM Triple\nWHERE p = 'foaf:name') as q1\nLEFT OUTER JOIN (SELECT s as x, p as foafmbox, o as mbox\nFROM Triple\nWHERE p = 'foaf:mbox') as q2\nON (q1.x=q2.x or q1.x=Null or q2.x=Null)) as q1\nLEFT OUTER JOIN (SELECT s as x, p as foafhomepage, o as hpage\nFROM Triple\nWHERE p = 'foaf:homepage') as q2\nON (q1.x=q2.x or q1.x=Null or q2.x=Null)"""

	def filterAndTest(self):
		""">>> translate('''SELECT  ?title ?price WHERE   { ?x ns:price ?price . FILTER (?price < 30.5 && ?price != 10 || ?price = -1) }''', True)
SELECT o as price\nFROM Triple\nWHERE p = 'ns:price' AND ( o < 30.5 AND o != 10 OR o = -1 )"""

	def filterBoundTest(self):
		""">>> translate('''SELECT  ?x ?price WHERE { ?x ns:price ?price . FILTER ( BOUND(?price) ) }''', True)
SELECT s as x, o as price\nFROM Triple\nWHERE p = 'ns:price' AND o IS NOT null"""

	def filterBoundORTest(self):
		""">>> translate('''SELECT  ?x ?price WHERE { ?x ns:price ?price . FILTER ( BOUND(?price) && ?price = 0 ) }''', True)
SELECT s as x, o as price\nFROM Triple\nWHERE p = 'ns:price' AND ( o IS NOT null AND o = 0 )"""

	def filterBetweenTriBlocksTest(self):
		""">>> translate('''SELECT  ?title ?price WHERE   { ?x ns:price ?price . FILTER (?price < 30.5) ?x dc:title ?title . }''', True)
SELECT title, price\nFROM (SELECT s as x, p as dctitle, o as title\nFROM Triple\nWHERE p = 'dc:title') as q1\nINNER JOIN (SELECT s as x, p as nsprice, o as price\nFROM Triple\nWHERE p = 'ns:price') as q2\nON (q1.x=q2.x or q1.x=Null or q2.x=Null)\nWHERE price < 30.5"""


if __name__ == "__main__":
	import doctest

	# run translator in test mode
	load_yaml(True)
	init_sqlite(True)

	doctest.testmod()

	doctest.testfile('cases/chebotko_cases.test')
	doctest.testfile('cases/W3C_cases.test')
	doctest.testfile('cases/manual.test')
