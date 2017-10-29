from setuptools import setup

setup(name='SPARQLToSQL',
      description='An SPARQL-to-SQL translator',
      long_description='An SPARQL-to-SQL translator based on a semantics-preserving translation approach by Artem Chebotko',
      version='1.0.2',
      url='https://github.com/munkhbayar17/sparql-to-sql',
      author='M. Nergui',
      author_email='muunuu17@gmail.com',
      license='Apache2',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Education',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3'
      ],
      packages=['SPARQLToSQL'],
      install_requires=[
          'Flask',
          'sqlparse',
          'rdflib'
      ],
      python_requires='>=3.6',
      entry_points={
          'console_scripts': [
              'encrypt=SPARQLToSQL.translator:translate'
          ]
      },
      include_package_data=True
      )
