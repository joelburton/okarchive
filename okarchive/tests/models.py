import unittest

from okarchive.tests import _initTestingDB, DBSession

class TestModel(unittest.TestCase):
    def setUp(self):
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()

    def test_journals(self):
        from ..models import Journals, Journal

        journals = Journals()

        db = (DBSession.query(Journal).one())
        self.assertEqual(journals['distractionbike'].name, 'distractionbike')
        self.assertEqual(journals['distractionbike'], db)
        self.assertSequenceEqual([j for j in journals.journals], [db])
        self.assertSequenceEqual(journals.keys(), ['distractionbike'])
        self.assertSequenceEqual(journals.values(), [db])
        self.assertSequenceEqual(journals.items(), [('distractionbike', db)])

        self.assertRaises(KeyError, lambda: journals['nosuch'])

        def _delete(key):
            del journals[key]

        self.assertRaises(NotImplementedError, lambda: _delete('somekey'))

        def _add(key):
            journals[key] = None

        self.assertRaises(NotImplementedError, lambda: _add('somekey'))


    def test_journal(self):
        from ..models import Journal

        journal = (DBSession
                   .query(Journal)
                   .filter(Journal.name == 'distractionbike')
                   .one())
        self.assertEqual(journal.name, 'distractionbike')
        self.assertEqual(len(journal.posts), 1)

    def test_journal_posts(self):
        from ..models import Journal, Post

        journal = (DBSession
                   .query(Journal)
                   .filter(Journal.name == 'distractionbike')
                   .one())
        post1 = (DBSession
                 .query(Post)
                 .one())

        self.assertSequenceEqual(journal.keys(), [1])
        self.assertSequenceEqual(journal.values(), [post1])
        self.assertSequenceEqual(journal.items(), [(1, post1)])

        del journal[1]
        self.assertSequenceEqual(journal.keys(), [])
        self.assertSequenceEqual(list(DBSession.query(Post)), [])

        post2 = Post(title='test', journal_name=journal.name)
        journal[1] = post2
        self.assertSequenceEqual(journal.keys(), [1])
        self.assertSequenceEqual(list(DBSession.query(Post)), [post2])

        # Test adding a post with mismatch
        post2 = Post(title='test', journal_name='x')

        def _set(id, post):
            journal[id] = post

        self.assertRaises(ValueError, _set, 1, post2)

    def test_journal_add_post_by_attributes(self):
        from ..models import Journal

        journal = (DBSession
                   .query(Journal)
                   .filter(Journal.name == 'distractionbike')
                   .one())
        journal.add_post(title='Foo', _flush=True)
        self.assertEquals(len(journal.posts), 2)

    def test_journal_add_post_by_object(self):
        from ..models import Journal, Post

        journal = (DBSession
                   .query(Journal)
                   .filter(Journal.name == 'distractionbike')
                   .one())
        post = Post(title='Foo')
        journal.add_post(post)
        self.assertEquals(len(journal.posts), 2)

    def test_posts(self):
        from ..models import Post

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
        from ..models import Comment

        comment = (DBSession
                   .query(Comment)
                   .filter(Comment.id == 1)
                   .one())
        self.assertEqual(comment.user_id, 'bob')
        self.assertEqual(comment.text, 'First Comment')
        self.assertEqual(comment.hidden, False)
        self.assertEqual(comment.post.id, 1)


    def test_post_add_comment_by_attributes(self):
        from ..models import Post

        post = (DBSession
                .query(Post)
                .one())
        post.add_comment(text='Foo', user_id='bob', _flush=True)
        self.assertEquals(len(post.comments), 2)

    def test_post_add_comment_by_object(self):
        from ..models import Post, Comment

        post = (DBSession
                .query(Post)
                .one())

        comment = Comment(text='Foo', user_id='bob')
        post.add_comment(comment)
        self.assertEquals(len(post.comments), 2)

    def test_user(self):
        from ..models import User

        user = (DBSession
                .query(User)
                .filter(User.name == 'distractionbike')
                .one())
        self.assertEqual(user.name, 'distractionbike')
        self.assertTrue(user.verifyPassword('secret'))
        self.assertEqual(user.password_md5, '5ebe2294ecd0e0f08eab7690d2a6ee69')

    def test_post_comments(self):
        from ..models import Post, Comment

        post = (DBSession
                .query(Post)
                .one())
        comment1 = (DBSession
                    .query(Comment)
                    .one())

        self.assertSequenceEqual(post.keys(), [1])
        self.assertSequenceEqual(post.values(), [comment1])
        self.assertSequenceEqual(post.items(), [(1, comment1)])

        del post[1]
        self.assertSequenceEqual(post.keys(), [])
        self.assertSequenceEqual(list(DBSession.query(Comment)), [])

        comment2 = Comment(text='test', user_id='bob', post_id=post.id)
        post[1] = comment2
        self.assertSequenceEqual(post.keys(), [1])
        self.assertSequenceEqual(list(DBSession.query(Comment)), [comment2])

        # Test adding a comment with mismatch
        comment2 = Comment(text='test', user_id='bob', post_id=99)

        def _set(id, comment):
            post[id] = comment

        self.assertRaises(ValueError, _set, 1, comment2)
