from . import BaseDatabaseTest


class BaseFunctionalTest(BaseDatabaseTest):
    def setUp(self):
        from okarchive import main
        from webtest import TestApp

        settings = {'sqlalchemy.url': 'sqlite://'}
        app = main({}, **settings)
        self.testapp = TestApp(app)

        BaseDatabaseTest.setUp(self)

    def tearDown(self):
        del self.testapp
        BaseDatabaseTest.tearDown(self)

    def _login(self):
        self.addUser()
        # Login and follow redirection
        return self.testapp.post(
            '/login',
            {'login': 'distractionbike',
             'password': 'secret',
             'form.submitted': 1},
            status=302).follow()


class HomepageTest(BaseFunctionalTest):
    def test_view(self):
        res = self.testapp.get('/', status=200)
        self.assertIn('<a href="/journals">Journals</a>', res)

        res2 = res.click('Journals')
        self.assertIn('<h1>Journals</h1>', res2)


class JournalsPageTest(BaseFunctionalTest):
    def test_view(self):
        self.addJournal()

        res = self.testapp.get('/journals', status=200)
        self.assertIn(
            '<a href="http://localhost/journals/distractionbike/">'
            'distractionbike</a>', res)


class JournalTest(BaseFunctionalTest):
    def test_journal_view_unauth(self):
        self.addAll()

        res = self.testapp.get('/journals/distractionbike', status=200)
        self.assertIn('<h1>distractionbike</h1>', res)
        self.assertNotIn(
            'href="http://localhost/journals/distractionbike/add">Add post',
            res)
        self.assertIn(
            '<a href="http://localhost/journals/distractionbike/1/">',
            res)

    def test_journal_view_auth(self):
        self.addAll()

        self._login()
        res = self.testapp.get('/journals/distractionbike', status=200)
        self.assertIn('<h1>distractionbike</h1>', res)
        self.assertIn(
            'href="http://localhost/journals/distractionbike/add">Add post',
            res)
        self.assertIn(
            '<a href="http://localhost/journals/distractionbike/1/">',
            res)


class JournalAddPostTest(BaseFunctionalTest):
    def test_add_post_unauth(self):
        self.addJournal()

        res = self.testapp.get('/journals/distractionbike')
        self.assertNotIn('Add post', res)

        res2 = self.testapp.get('/journals/distractionbike/add')
        self.assertSequenceEqual(res2.status, '200 OK')
        self.assertIn('Please sign in', res2)


    def test_add_post_bad_validation(self):
        self.addJournal()
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
        self.addJournal()
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


class PostViewTest(BaseFunctionalTest):

    def test_post_view_unauth(self):
        self.addAll()

        res = self.testapp.get('/journals/distractionbike/1', status=200)
        self.assertIn('<h1>First Post</h1>', res)
        self.assertNotIn(
            'href="http://localhost/journals/distractionbike/1/edit"',
            res)
        self.assertNotIn('#delete-post-modal"', res)

    def test_post_view_auth(self):
        self.addAll()

        self._login()
        res = self.testapp.get('/journals/distractionbike/1', status=200)
        self.assertIn('<h1>First Post</h1>', res)
        self.assertIn(
            'href="http://localhost/journals/distractionbike/1/edit"',
            res)
        self.assertIn('#delete-post-modal', res)


class PostEditTest(BaseFunctionalTest):
    def test_edit_post_unauth(self):
        self.addAll()

        res = self.testapp.get('/journals/distractionbike/1')
        self.assertNotIn('Edit', res)

        res2 = self.testapp.get('/journals/distractionbike/1/edit')
        self.assertSequenceEqual(res2.status, '200 OK')
        self.assertIn('Please sign in', res2)

    def test_edit_post_bad_validation(self):
        self.addAll()
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
        self.addAll()
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

    def test_edit_post_cancel(self):
        self.addAll()
        res = self._login()

        res = self.testapp.get('/journals/distractionbike/1')
        res2 = res.click('Edit')
        self.assertSequenceEqual(res2.status, '200 OK')
        self.assertIn('<h1>Edit Post</h1>', res2)

        form = res2.forms['edit-post']
        form['title'] = 'My 2nd Post'
        res3 = form.submit('cancel').follow()

        self.assertNotIn('<h1>My 2nd Post</h1>', res3)
        self.assertIn('<h1>First Post</h1>', res3)



class PostDeleteTest(BaseFunctionalTest):
    def test_del_post_unauth(self):
        self.addAll()

        res = self.testapp.get('/journals/distractionbike/1')
        self.assertNotIn('post-delete-btn', res)

        res2 = self.testapp.get('/journals/distractionbike/1/delete')
        self.assertSequenceEqual(res2.status, '200 OK')
        self.assertIn('Please sign in', res2)

    def test_edit_post_delete(self):
        self.addAll()
        res = self._login()

        res = self.testapp.get('/journals/distractionbike/1')
        form = res.forms['post-delete']
        res2 = form.submit('post-delete-btn').follow()
        self.assertNotIn('First Post', res2)
        self.assertIn('There are no posts in this journal you can read.', res2)


class LoginLogoutTest(BaseFunctionalTest):
    def test_login_incorrect(self):
        self.addUser()

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
        self.addUser()

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


