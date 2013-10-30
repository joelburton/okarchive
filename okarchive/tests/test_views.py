from pyramid import testing
#from pyramid.request import Request

from . import BaseDatabaseTest, DBSession

from okarchive.views import (
    HomeView,
    JournalsView,
    JournalView,
    PostView,
    CommentView,
    LoginLogoutView,
)
from okarchive.models import (
    journals,
    Post,
)

class BaseTestView(BaseDatabaseTest):
    def setUp(self):
        self.config = testing.setUp()

        BaseDatabaseTest.setUp(self)

    def tearDown(self):
        BaseDatabaseTest.tearDown(self)
        testing.tearDown()


class TestHomeView(BaseTestView):
    def test_it(self):
        request = testing.DummyRequest()
        view = HomeView(request)
        info = view.view()

        self.assertIn('logged_in', info)


class TestJournalsView(BaseTestView):
    def test_it(self):
        request = testing.DummyRequest()
        view = JournalsView(journals, request)
        info = view.view()

        self.assertIs(info['journals'], journals)


class TestJournalView(BaseTestView):
    def test_it(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest()
        view = JournalView(journal, request)
        info = view.view()

        self.assertEqual(info['journal_name'], 'distractionbike')
        self.assertEqual(len(info['posts']), 1)
        self.assertEqual(info['add_url'],
                         'http://example.com/journals/distractionbike/add')


class TestJournalViewWithSecurity(BaseTestView):
    def setUp(self):
        BaseTestView.setUp(self)

        from pyramid.authentication import AuthTktAuthenticationPolicy
        from pyramid.authorization import ACLAuthorizationPolicy

        authn_policy = AuthTktAuthenticationPolicy(
            secret='sosecret',
            hashalg='sha512',
        )
        authz_policy = ACLAuthorizationPolicy()
        self.config.set_authorization_policy(authz_policy)
        self.config.set_authentication_policy(authn_policy)

    def test_view_no_add_btn(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest()
        view = JournalView(journal, request)
        info = view.view()

        self.assertEqual(info['journal_name'], 'distractionbike')
        self.assertEqual(len(info['posts']), 1)
        self.assertEqual(info['add_url'], None)


class TestJournalViewPostAdd(BaseTestView):
    def test_form(self):
        journal = self.addJournal()

        request = testing.DummyRequest()
        request.matchdict['journal_name'] = 'distractionbike'

        view = JournalView(journal, request)
        info = view.add()

        self.assertEqual(info['post'].title, 'Title')

    def test_add(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest(
            post={'add': 1,
                  'title': 'Yo',
                  'lede': 'lede',
                  'text': 'There'})
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

    def test_add_validation_fail(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest(
            post={'add': 1,
                  'title': '',
                  'lede': 'lede',
                  'text': 'There'})
        request.matchdict['journal_name'] = 'distractionbike'
        view = JournalView(journal, request)
        info = view.add()

        self.assertSequenceEqual(sorted(info.keys()),
                                 ['form', 'journal_url', 'logged_in', 'post',
                                  'registry', 'title'])


class TestPostView(BaseTestView):
    def test_it(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest()
        view = PostView(post, request)
        info = view.view()

        self.assertEqual(info['journal_url'],
                         'http://example.com/journals/distractionbike/')
        self.assertEqual(info['edit_url'],
                         'http://example.com/journals/distractionbike/1/edit')
        self.assertEqual(info['delete_url'],
                         'http://example.com/journals/distractionbike/1/delete')


class TestPostViewWithSecurity(BaseTestView):
    def setUp(self):
        BaseTestView.setUp(self)

        from pyramid.authentication import AuthTktAuthenticationPolicy
        from pyramid.authorization import ACLAuthorizationPolicy

        authn_policy = AuthTktAuthenticationPolicy(
            secret='sosecret',
            hashalg='sha512',
        )
        authz_policy = ACLAuthorizationPolicy()
        self.config.set_authorization_policy(authz_policy)
        self.config.set_authentication_policy(authn_policy)

    def test_view_no_edit_del_buttons(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest()
        view = PostView(post, request)
        info = view.view()

        self.assertEqual(info['journal_url'],
                         'http://example.com/journals/distractionbike/')
        self.assertEqual(info['edit_url'], None)
        self.assertEqual(info['delete_url'], None)


class TestPostEdit(BaseTestView):
    def test_form(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest()
        view = PostView(post, request)
        info = view.edit()

        self.assertEqual(info['post'].title, 'First Post')

    def test_edit(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest(
            post={'edit': 1,
                  'title': 'Yo',
                  'lede': 'lede',
                  'text': 'There'})
        view = PostView(post, request)
        info = view.edit()

        self.assertEqual(info.status, '302 Found')
        self.assertEqual(info.location,
                         'http://example.com/journals/distractionbike/1/')
        self.assertTrue(request.session.peek_flash(), [('success', 'Edited.')])
        post = (DBSession
                .query(Post)
                .filter(Post.id == 1)
                .one())
        self.assertEqual(post.title, 'Yo')
        self.assertEqual(post.lede, 'lede')
        self.assertEqual(post.text, 'There')

    def test_edit_validation_fail(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest(
            post={'edit': 1,
                  'title': '',  # blank title is invalid
                  'lede': 'lede',
                  'text': 'There'})
        view = PostView(post, request)
        info = view.edit()

        self.assertSequenceEqual(sorted(info.keys()),
                                 ['form', 'journal_url', 'logged_in', 'post',
                                  'registry', 'title'])

    def test_edit_validation_cancel(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest(
            post={'cancel': 1,
                  'title': 'Title',
                  'lede': 'lede',
                  'text': 'There'})
        view = PostView(post, request)
        info = view.edit()

        self.assertEqual(info.status, '302 Found')
        self.assertEqual(info.location,
                         'http://example.com/journals/distractionbike/1/')
        self.assertTrue(request.session.peek_flash(),[('info', 'Cancelled.')])

    def test_delete_post(self):
        journal = self.addJournal()
        post = self.addPost()

        request = testing.DummyRequest()
        view = PostView(post, request)
        info = view.delete()

        self.assertEqual(info.status, '302 Found')
        self.assertEqual(info.location,
                         'http://example.com/journals/distractionbike/')
        self.assertTrue(request.session.peek_flash(), [('danger', 'Deleted.')])
        self.assertEqual(DBSession.query(Post).count(), 0)


class TestCommentView(BaseTestView):
    def test_it(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()

        request = testing.DummyRequest()
        view = CommentView(comment, request)
        info = view.view()

        self.assertEqual(info.body, b'First Comment')

    def test_publish(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()
        comment.hidden = True

        request = testing.DummyRequest()
        view = CommentView(comment, request)
        info = view.publish()

        self.assertFalse(comment.hidden)

    def test_hide(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()
        comment.hidden = False

        request = testing.DummyRequest()
        view = CommentView(comment, request)
        info = view.reject()

        self.assertTrue(comment.hidden)


class TestLoginLogoutView(BaseTestView):
    def test_form_referred(self):
        request = testing.DummyRequest(url='http://example.com/tried-here')
        view = LoginLogoutView(request)
        info = view.login()

        self.assertEqual(info['url'], 'http://example.com/login')
        self.assertEqual(info['came_from'], 'http://example.com/tried-here')
        self.assertEqual(info['login'], '')
        self.assertEqual(info['password'], '')

    def test_form_directly_visited(self):
        request = testing.DummyRequest(url='http://example.com/login')
        view = LoginLogoutView(request)
        info = view.login()

        self.assertEqual(info['url'], 'http://example.com/login')
        self.assertEqual(info['came_from'], '/')
        self.assertEqual(info['login'], '')
        self.assertEqual(info['password'], '')

    def test_login_success(self):
        self.addUser()

        request = testing.DummyRequest(
            params={'login':'distractionbike',
                    'password':'secret',
                    'form.submitted': 1}
        )
        view = LoginLogoutView(request)
        info = view.login()

        self.assertEqual(info.status, '302 Found')
        self.assertEqual(info.location,
                         'http://example.com')
        self.assertTrue(
            request.session.peek_flash(), [('success', 'Signed in.')])

    def test_login_fail(self):
        self.addUser()

        request = testing.DummyRequest(
            params={'login': 'distractionbike',
                    'password': 'wrong',
                    'form.submitted': 1}
        )
        view = LoginLogoutView(request)
        info = view.login()

        self.assertEqual(info['url'], 'http://example.com/login')
        self.assertEqual(info['came_from'], 'http://example.com')
        self.assertEqual(info['login'], 'distractionbike')
        self.assertEqual(info['password'], 'wrong')
        self.assertTrue(
            request.session.peek_flash(), [('danger', 'Failed sign in.')])

    def test_logout(self):
        request = testing.DummyRequest()
        view = LoginLogoutView(request)
        info = view.logout()

        self.assertEqual(info.status, '302 Found')
        self.assertEqual(info.location, 'http://example.com')
        self.assertTrue(
            request.session.peek_flash(), [('success', 'Signed out.')])


