import unittest


class UnitTest(unittest.TestCase):
	def test_GenPRSQL(self):
		triplePattern = TriplePattern(Variable('y'), IRI(':knows'), 'x')
		pr_list = []
		pr_list.append(SQLProject('s', 'y'))
		pr_list.append(SQLProject('p', 'knows'))
		pr_list.append(SQLProject('o', 'x'))
		testpr_list = genPRSQL(triplePattern)
		self.assertEqual(testpr_list, pr_list)


if __name__ == "__main__":
	unittest.main()
