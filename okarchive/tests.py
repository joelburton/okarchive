import unittest
import transaction

from pyramid import testing

from .models import DBSession


class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            Journal,
            Post
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            journal = Journal(name='distractionbike')
            DBSession.add(journal)
            post = Post(journal_name='distractionbike', title='First Post')
            DBSession.add(post)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['one'].name, 'distractionbike')
        self.assertEqual(info['project'], 'okarchive')
