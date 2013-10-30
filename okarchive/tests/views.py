import unittest

from pyramid import testing

from . import _initTestingDB, DBSession


class TestJournalView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from ..views import JournalView
        from ..models import Journal

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
        self.config = testing.setUp()
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from ..views import PostView
        from ..models import Post

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


class TestCommentView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from ..views import CommentView
        from ..models import Comment

        request = testing.DummyRequest()
        comment = (DBSession
                   .query(Comment)
                   .one())
        view = CommentView(comment, request)
        info = view.view()
        self.assertEqual(info.body, b'First Comment')

    def test_publish(self):
        from ..views import CommentView
        from ..models import Comment

        request = testing.DummyRequest()
        comment = (DBSession
                   .query(Comment)
                   .one())
        comment.hidden = True
        view = CommentView(comment, request)
        info = view.publish()
        self.assertFalse(comment.hidden)

    def test_hide(self):
        from ..views import CommentView
        from ..models import Comment

        request = testing.DummyRequest()
        comment = (DBSession
                   .query(Comment)
                   .one())
        comment.hidden = False
        view = CommentView(comment, request)
        info = view.reject()
        self.assertTrue(comment.hidden)


class TestPostAdd(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_form(self):
        from ..views import JournalView
        from ..models import Journal

        request = testing.DummyRequest()
        journal = (DBSession
                   .query(Journal)
                   .one())
        request.matchdict['journal_name'] = 'distractionbike'
        view = JournalView(journal, request)
        info = view.add()
        self.assertEqual(info['post'].title, 'Title')

    def test_add(self):
        from ..views import JournalView
        from ..models import Post, Journal

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
        self.config = testing.setUp()
        _initTestingDB()


    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_form(self):
        from ..views import PostView
        from ..models import Post

        request = testing.DummyRequest()
        post = (DBSession
                .query(Post)
                .one())
        view = PostView(post, request)
        info = view.edit()
        self.assertEqual(info['post'].title, 'First Post')

    def test_edit(self):
        from ..views import PostView
        from ..models import Post

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
