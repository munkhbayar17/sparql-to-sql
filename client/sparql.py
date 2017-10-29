import pip

if __name__ == '__main__':
	pip.main(['install', 'SPARQLToSQL'])
	from SPARQLToSQL import main
	main.init();