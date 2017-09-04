from setuptools import setup

setup(name='sparql',
      description='An SPARQL-to-SQL translator',
      long_description='An SPARQL-to-SQL translator based on a semantics-preserving translation approach by Artem Chebotko',
      version='0.1.0',
      url='https://github.com/munkhbayar17/sparql-to-sql',
      author='M. Nergui',
      author_email='muunuu17@gmail.com',
      license='Apache2',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Students',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3'
      ],
      packages=['sparql'],
      install_requires=[
          'PyYAML>=3.11'
      ],
      entry_points={
          'console_scripts': [
              'encrypt=sparql.main:translate'
          ]
      }
)