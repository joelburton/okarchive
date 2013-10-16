okarchive
=========

OkArchive is a web application that simulates some of the functionality of OkCupid's retired
journals. It was written as a place where users could upload their journal archives and
continue the journaling community.

This is written using the Pyramid web application framework. It can store its data in any
relational database that SQLAlchemy can use. It was developed and tested with SQLite and
PostgreSQL.


Getting Started
---------------

1. cd <directory containing this file>

2. $venv/bin/python setup.py develop

3. $venv/bin/initialize_okarchive_db development.ini

4. $venv/bin/pserve development.ini


Credits
-------

Copyright 2013 by Joel Burton <joel@joelburton.com>