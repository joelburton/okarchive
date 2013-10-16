import unittest
import transaction

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from .models import DBSession


def _initTestingDB():
    from sqlalchemy import create_engine
    from okarchive.models import (
        DBSession,
        Base,
        Journal,
        Post,
        Comment,
        )

    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        journal = Journal(name='distractionbike')
        DBSession.add(journal)
        post = Post(journal_name='distractionbike', title='First Post')
        DBSession.add(post)
        DBSession.flush()
        comment = Comment(post_id=post.id, user_id='bob', text='First Comment')
        DBSession.add(comment)
    return DBSession


class TestModel(unittest.TestCase):
    def setUp(self):
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()

    def test_journal(self):
        from .models import Journal
        journal = DBSession.query(Journal).filter(Journal.name == 'distractionbike').one()
        self.assertEqual(journal.name, 'distractionbike')
        self.assertEqual(len(journal.posts), 1)

    def test_posts(self):
        from .models import Post
        post = DBSession.query(Post).filter(Post.id == 1).one()
        self.assertEqual(post.journal_name, 'distractionbike')
        self.assertEqual(post.title, 'First Post')
        self.assertEqual(post.journal.name, 'distractionbike')
        self.assertEqual(len(post.comments), 1)

    def test_comments(self):
        from .models import Comment
        comment = DBSession.query(Comment).filter(Comment.id == 1).one()
        self.assertEqual(comment.user_id, 'bob')
        self.assertEqual(comment.text, 'First Comment')
        self.assertEqual(comment.hidden, False)
        self.assertEqual(comment.post.id, 1)


class TestJournalView(unittest.TestCase):
    def setUp(self):
        from okarchive import add_routes
        self.config = testing.setUp()
        add_routes(self.config)
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_404(self):
        from .views import JournalView
        request = testing.DummyRequest()
        request.matchdict['journal_name'] = 'mr-nobody'
        view = JournalView(request)
        self.assertRaises(HTTPNotFound, view.view)

    def test_it(self):
        from .views import JournalView
        request = testing.DummyRequest()
        request.matchdict['journal_name'] = 'distractionbike'
        view = JournalView(request)
        info = view.view()
        self.assertEqual(info['journal_name'], 'distractionbike')
        self.assertEqual(len(info['posts']), 1)


class TestPostView(unittest.TestCase):
    def setUp(self):
        from okarchive import add_routes
        self.config = testing.setUp()
        add_routes(self.config)
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_404(self):
        from .views import PostView
        request = testing.DummyRequest()
        request.matchdict['journal_name'] = 'mr-nobody'
        request.matchdict['post_id'] = 99
        view = PostView(request)
        self.assertRaises(HTTPNotFound, view.view)

    def test_it(self):
        from .views import PostView
        request = testing.DummyRequest()
        request.matchdict['journal_name'] = 'distractionbike'
        request.matchdict['post_id'] = 1
        view = PostView(request)
        info = view.view()
        self.assertEqual(info['journal_url'], 'http://example.com/journals/distractionbike')
        self.assertEqual(info['edit_url'], 'http://example.com/journals/distractionbike/1/edit')


class TestPostAdd(unittest.TestCase):
    def setUp(self):
        from okarchive import add_routes
        self.config = testing.setUp()
        add_routes(self.config)
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_form(self):
        from .views import PostView

        request = testing.DummyRequest()
        request.matchdict['journal_name'] = 'distractionbike'
        view = PostView(request)
        info = view.add()
        self.assertEqual(info['post'].title, 'Title')

    def test_add(self):
        from .views import PostView
        from .models import Post

        request = testing.DummyRequest(post={'add':1, 'title':'Yo', 'text':'There'})
        request.matchdict['journal_name'] = 'distractionbike'
        view = PostView(request)
        info = view.add()
        self.assertEqual(info.status, '302 Found')
        self.assertEqual(info.location, 'http://example.com/journals/distractionbike/2')

        post = DBSession.query(Post).filter(Post.id == 2).one()
        self.assertEqual(post.title, 'Yo')
        self.assertEqual(post.text, 'There')


class TestPostEdit(unittest.TestCase):
    def setUp(self):
        from okarchive import add_routes
        self.config = testing.setUp()
        add_routes(self.config)
        _initTestingDB()


    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_form(self):
        from .views import PostView

        request = testing.DummyRequest()
        request.matchdict['journal_name'] = 'distractionbike'
        request.matchdict['post_id'] = 1
        view = PostView(request)
        info = view.edit()
        self.assertEqual(info['post'].title, 'First Post')

    def test_edit(self):
        from .views import PostView
        from .models import Post

        request = testing.DummyRequest(post={'edit': 1, 'title': 'Yo', 'text': 'There'})
        request.matchdict['journal_name'] = 'distractionbike'
        request.matchdict['post_id'] = 1
        view = PostView(request)
        info = view.edit()
        self.assertEqual(info.status, '302 Found')
        self.assertEqual(info.location, 'http://example.com/journals/distractionbike/1')

        post = DBSession.query(Post).filter(Post.id == 1).one()
        self.assertEqual(post.title, 'Yo')
        self.assertEqual(post.text, 'There')


class FunctionalTests(unittest.TestCase):

    def setUp(self):
        from okarchive import main

        settings = {'sqlalchemy.url': 'sqlite://'}
        app = main({}, **settings)
        from webtest import TestApp

        self.testapp = TestApp(app)
        _initTestingDB()

    def tearDown(self):
        del self.testapp
        from okarchive.models import DBSession

        DBSession.remove()

    def test_journal_view(self):
        res = self.testapp.get('/journals/distractionbike', status=200)
        self.assertTrue(b'<h1>distractionbike</h1>' in res.body)
        self.assertTrue(b'<a href="http://localhost/journals/distractionbike/add">Add post</a>'
                in res.body)
        self.assertTrue(b'<a href="http://localhost/journals/distractionbike/1">'
                in res.body)

    def test_post_view(self):
        res = self.testapp.get('/journals/distractionbike/1', status=200)
        self.assertTrue(b'<h1>First Post</h1>' in res.body)
        self.assertTrue(b'<a href="http://localhost/journals/distractionbike/1/edit">Edit post'
                in res.body)

    # FIXME: add func tests for post-add, post-edit, and for validation problems