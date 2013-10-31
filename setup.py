import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt'), encoding='utf-8').read()
CHANGES = open(os.path.join(here, 'CHANGES.txt'), encoding='utf-8').read()

requires = [
    'pyramid>=1.5a2',
    'SQLAlchemy',
    'transaction',
    'pyramid_chameleon',
    'pyramid_tm',
    'pyramid_debugtoolbar>=1.0.9',
    'zope.sqlalchemy',
    'waitress',
    'psycopg2',
    'deform>=2.0a2',
    'colanderalchemy',
    ]

testing_extras = ['nose', 'coverage', 'webtest']
docs_extras = ['Sphinx']

setup(name='okarchive',
      version='0.1',
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
