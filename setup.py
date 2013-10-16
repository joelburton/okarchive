import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'psycopg2',
    'deform',
    'colanderalchemy',
    ]

testing_extras = ['nose', 'coverage']
docs_extras = ['Sphinx']

setup(name='okarchive',
      version='0.0',
      description='okarchive',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Joel Burton',
      author_email='joel@joelburton.com',
      url='http://joelburton.com',
      keywords='web wsgi bfg pylons pyramid okcupid blog journal',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='okarchive',
      extras_require={
          'testing': testing_extras,
          'docs': docs_extras,
      },
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = okarchive:main
      [console_scripts]
      initialize_okarchive_db = okarchive.scripts.initializedb:main
      """,
      )
