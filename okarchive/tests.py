"""OkArchive tests."""

import unittest
import transaction

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import (
    Allow,
    Everyone,
)

from .models import DBSession


class AllAllowedRootFactory:
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Everyone, 'add'),
        (Allow, Everyone, 'edit'),
        (Allow, Everyone, 'delete'),
    ]

resource = AllAllowedRootFactory()


def _initTestingDB():
    import hashlib
    from sqlalchemy import create_engine
    from okarchive.models import (
        Base,
        Journal,
        Post,
        Comment,
        User,
        )

    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)

    with transaction.manager:
        md5 = hashlib.md5('secret'.encode()).hexdigest()
        user = User(name='distractionbike', password_md5=md5)
        DBSession.add(user)
        journal = Journal(name='distractionbike')
        DBSession.add(journal)
        post = Post(
            journal_name='distractionbike',
            title='First Post',
            lede='First lede',
            text='<b>My body</b>')
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

        journal = (DBSession
                   .query(Journal)
                   .filter(Journal.name == 'distractionbike')
                   .one())
        self.assertEqual(journal.name, 'distractionbike')
        self.assertEqual(len(journal.posts), 1)

    def test_posts(self):
        from .models import Post

        post = (DBSession
                .query(Post)
                .filter(Post.id == 1)
                .one())
        self.assertEqual(post.journal_name, 'distractionbike')
        self.assertEqual(post.title, 'First Post')
        self.assertEqual(post.lede, 'First lede')
        self.assertEqual(post.journal.name, 'distractionbike')
        self.assertEqual(len(post.comments), 1)

    def test_comments(self):
        from .models import Comment

        comment = (DBSession
                   .query(Comment)
                   .filter(Comment.id == 1)
                   .one())
        self.assertEqual(comment.user_id, 'bob')
        self.assertEqual(comment.text, 'First Comment')
        self.assertEqual(comment.hidden, False)
        self.assertEqual(comment.post.id, 1)

    def test_user(self):
        from .models import User

        user = (DBSession
                .query(User)
                .filter(User.name == 'distractionbike')
                .one())
        self.assertEqual(user.name, 'distractionbike')
        self.assertTrue(user.verifyPassword('secret'))
        self.assertEqual(user.password_md5, '5ebe2294ecd0e0f08eab7690d2a6ee69')


class TestJournalView(unittest.TestCase):
    def setUp(self):
        from . import add_routes

        self.config = testing.setUp()
        add_routes(self.config)
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import JournalView
        from .models import Journal

        journal = (DBSession
                   .query(Journal)
                   .one())

        request = testing.DummyRequest()
        view = JournalView(journal, request)
        info = view.view()
        self.assertEqual(info['journal_name'], 'distractionbike')
        self.assertEqual(len(info['posts']), 1)


class TestPostView(unittest.TestCase):
    def setUp(self):
        from . import add_routes

        self.config = testing.setUp()
        add_routes(self.config)
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import PostView
        from .models import Post

        request = testing.DummyRequest()
        post = (DBSession
                .query(Post)
                .one())
        view = PostView(post, request)
        info = view.view()
        self.assertEqual(info['journal_url'],
                         'http://example.com/journals/distractionbike/')
        self.assertEqual(info['edit_url'],
                         'http://example.com/journals/distractionbike/1/edit')


class TestPostAdd(unittest.TestCase):
    def setUp(self):
        from . import add_routes

        self.config = testing.setUp()
        add_routes(self.config)
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_form(self):
        from .views import JournalView
        from .models import Journal

        request = testing.DummyRequest()
        journal = (DBSession
                   .query(Journal)
                   .one())
        request.matchdict['journal_name'] = 'distractionbike'
        view = JournalView(journal, request)
        info = view.add()
        self.assertEqual(info['post'].title, 'Title')

    def test_add(self):
        from .views import JournalView
        from .models import Post, Journal

        request = testing.DummyRequest(
            post={'add': 1,
                  'title': 'Yo',
                  'lede': 'lede',
                  'text': 'There'})
        journal = (DBSession
                   .query(Journal)
                   .one())
        request.matchdict['journal_name'] = 'distractionbike'
        view = JournalView(journal, request)
        info = view.add()
        self.assertEqual(info.status, '302 Found')
        self.assertEqual(info.location,
                         'http://example.com/journals/distractionbike/2/')

        post = (DBSession
                .query(Post)
                .filter(Post.id == 2)
                .one())
        self.assertEqual(post.title, 'Yo')
        self.assertEqual(post.lede, 'lede')
        self.assertEqual(post.text, 'There')


class TestPostEdit(unittest.TestCase):
    def setUp(self):
        from . import add_routes

        self.config = testing.setUp()
        add_routes(self.config)
        _initTestingDB()


    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_form(self):
        from .views import PostView
        from .models import Post

        request = testing.DummyRequest()
        post = (DBSession
                .query(Post)
                .one())
        view = PostView(post, request)
        info = view.edit()
        self.assertEqual(info['post'].title, 'First Post')

    def test_edit(self):
        from .views import PostView
        from .models import Post

        request = testing.DummyRequest(
            post={'edit': 1,
                  'title': 'Yo',
                  'lede': 'lede',
                  'text': 'There'})
        post = (DBSession
                .query(Post)
                .one())
        view = PostView(post, request)
        info = view.edit()
        self.assertEqual(info.status, '302 Found')
        self.assertEqual(info.location,
                         'http://example.com/journals/distractionbike/1/')

        post = (DBSession
                .query(Post)
                .filter(Post.id == 1)
                .one())
        self.assertEqual(post.title, 'Yo')
        self.assertEqual(post.lede, 'lede')
        self.assertEqual(post.text, 'There')


class TestSecurity(unittest.TestCase):
    def setUp(self):
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()

    def test_authenticate(self):
        from .security import authenticate

        self.assertTrue(authenticate('distractionbike', 'secret'))

    def test_groups(self):
        from .security import group_finder

        self.assertSequenceEqual(group_finder('distractionbike',
                                              request=None),
                                 ['group:editors'])


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from . import main

        settings = {'sqlalchemy.url': 'sqlite://'}
        app = main({}, **settings)
        from webtest import TestApp

        self.testapp = TestApp(app)
        _initTestingDB()

    def tearDown(self):
        del self.testapp
        from .models import DBSession

        DBSession.remove()

    def _login(self):
        # Login and follow redirection
        return self.testapp.post(
            '/login',
            {'login': 'distractionbike',
             'password': 'secret',
             'form.submitted': 1},
            status=302).follow()

    def test_journal_view_unauth(self):
        res = self.testapp.get('/journals/distractionbike', status=200)
        self.assertIn('<h1>distractionbike</h1>', res)
        self.assertNotIn(
            'href="http://localhost/journals/distractionbike/add">Add post',
            res)
        self.assertIn(
            '<a href="http://localhost/journals/distractionbike/1/">',
            res)

    def test_journal_view_auth(self):
        self._login()
        res = self.testapp.get('/journals/distractionbike', status=200)
        self.assertIn('<h1>distractionbike</h1>', res)
        self.assertIn(
            'href="http://localhost/journals/distractionbike/add">Add post',
            res)
        self.assertIn(
            '<a href="http://localhost/journals/distractionbike/1/">',
            res)

    def test_post_view_unauth(self):
        res = self.testapp.get('/journals/distractionbike/1', status=200)
        self.assertIn('<h1>First Post</h1>', res)
        self.assertNotIn(
            'href="http://localhost/journals/distractionbike/1/edit"',
            res)
        self.assertNotIn('#delete-post-modal"', res)

    def test_post_view_auth(self):
        self._login()
        res = self.testapp.get('/journals/distractionbike/1', status=200)
        self.assertIn('<h1>First Post</h1>', res)
        self.assertIn(
            'href="http://localhost/journals/distractionbike/1/edit"',
            res)
        self.assertIn('#delete-post-modal', res)

    def test_login_incorrect(self):
        # Get login form
        res = self.testapp.get('/login', status=200)
        self.assertIn('Please sign in', res)
        self.assertNotIn('Failed sign in', res)
        # login with wrong password
        form = res.forms['login']
        form['login'].value = 'distractionbike'
        form['password'].value = 'wrong'
        res2 = form.submit('form.submitted')
        self.assertIn('Failed sign in', res2)
        self.assertNotIn('/logout">Sign out</a>', res2)

    def test_login_correct(self):
        # Get login form
        res = self.testapp.get('/login', status=200)
        self.assertIn('Please sign in', res)
        self.assertNotIn('Failed sign in', res)

        # Login with right password
        form = res.forms['login']
        form['login'].value = 'distractionbike'
        form['password'].value = 'secret'
        res2 = form.submit('form.submitted')
        self.assertNotIn('Failed sign in', res2)
        self.assertEqual(res2.status, '302 Found')

        # Get page on site and make sure we see logout button
        res3 = res2.follow()
        self.assertIn('/logout">Sign out</a>', res3)

    def test_logout(self):
        res = self._login()
        res2 = res.click('Sign out').follow()
        self.assertNotIn('/logout">Logout</a>', res2)

    def test_goto_journal(self):
        res = self.testapp.get('/journals')
        res2 = res.click('distractionbike')
        self.assertIn('<h1>distractionbike</h1>', res2)

    def test_add_post_bad_validation(self):
        res = self._login()
        res = self.testapp.get('/journals/distractionbike')
        res2 = res.click('Add post')
        self.assertSequenceEqual(res2.status, '200 OK')
        self.assertIn('<h1>Add Post</h1>', res2)

        form = res2.forms['add-post']
        # Do not fill in a title; this will cause validation error
        form['lede'] = 'New lede'
        form['text'] = '<b>My post</b>'
        res3 = form.submit('add')

        self.assertIn('There was a problem with your submission', res3)
        self.assertIn('New lede', res3)
        self.assertIn('<b>My post</b>', res3)

    def test_add_post_ok(self):
        res = self._login()
        res = self.testapp.get('/journals/distractionbike')
        res2 = res.click('Add post')
        self.assertSequenceEqual(res2.status, '200 OK')
        self.assertIn('<h1>Add Post</h1>', res2)

        form = res2.forms['add-post']
        form['title'] = 'My Title'
        form['lede'] = 'New lede'
        form['text'] = '<b>My post</b>'
        res3 = form.submit('add').follow()

        self.assertIn('<h1>My Title</h1>', res3)
        self.assertIn('New lede', res3)
        self.assertIn('<b>My post</b>', res3)

    def test_edit_post_bad_validation(self):
        res = self._login()
        res = self.testapp.get('/journals/distractionbike/1')
        res2 = res.click('Edit')
        self.assertSequenceEqual(res2.status, '200 OK')
        self.assertIn('<h1>Edit Post</h1>', res2)

        form = res2.forms['edit-post']
        # Clear title; this will cause validation error
        form['title'] = ''
        form['text'] = '<b>My 2nd body</b>'
        res3 = form.submit('edit')

        self.assertIn('There was a problem with your submission', res3)
        self.assertIn('First lede', res3)
        self.assertIn('<b>My 2nd body</b>', res3)

    def test_edit_post_ok(self):
        res = self._login()
        res = self.testapp.get('/journals/distractionbike/1')
        res2 = res.click('Edit')
        self.assertSequenceEqual(res2.status, '200 OK')
        self.assertIn('<h1>Edit Post</h1>', res2)

        form = res2.forms['edit-post']
        form['title'] = 'My 2nd Post'
        form['lede'] = '2nd lede'
        form['text'] = '<b>My 2nd body</b>'
        res3 = form.submit('edit').follow()

        self.assertIn('<h1>My 2nd Post</h1>', res3)
        self.assertIn('2nd lede', res3)
        self.assertIn('<b>My 2nd body</b>', res3)

