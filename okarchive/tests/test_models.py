import unittest

from pyramid.security import (
    Allow,
    Deny,
    Everyone,
    Authenticated,
)

from okarchive.tests import BaseDatabaseTest, DBSession
from okarchive.models import (
    Journals,
    Journal,
    Post,
    Comment,
    RootFactory,
    journals
)


class SiteRootTest(unittest.TestCase):
    def test_root(self):
        root = RootFactory(None)

        self.assertIs(root['journals'], journals)

class ModelBaseTest(BaseDatabaseTest):
    pass


class JournalsModelTest(ModelBaseTest):
    def test_journals(self):
        journal = self.addJournal()

        self.assertIs(journals['distractionbike'], journal)
        self.assertEqual(journal.name, 'distractionbike')
        self.assertSequenceEqual([j for j in journals.journals], [journal])
        self.assertSequenceEqual(journals.keys(), ['distractionbike'])
        self.assertSequenceEqual(journals.values(), [journal])
        self.assertSequenceEqual(journals.items(),
                                 [('distractionbike', journal)])

    def test_journal_traversal(self):
        journal = self.addJournal()

        self.assertEqual(journal.__name__, 'distractionbike')
        self.assertEqual(journal.__parent__, journals)

    def test_acl(self):
        journal = self.addJournal()

        self.assertSequenceEqual(
            journal.__acl__,
            [(Allow, Everyone, 'view'),
             (Allow, 'group:editors', ('edit', 'add', 'delete')),
              (Allow, 'distractionbike', ('edit', 'add', 'delete')),
            ])

    def test_journal_404(self):
        journal = self.addJournal()
        self.assertRaises(KeyError, lambda: journals['nosuch'])

    def test_delete_journal(self):
        journal = self.addJournal()

        def _delete(key):
            del journals[key]

        self.assertRaises(NotImplementedError, _delete, 'distractionbike')

    def test_add_journal(self):

        def _add(key):
            journals[key] = None

        self.assertRaises(NotImplementedError, _add, 'somekey')


class JournalModelTest(ModelBaseTest):
    def test_journal(self):
        journal = self.addJournal()

        self.assertEqual(journal.name, 'distractionbike')

    def test_journal_posts(self):
        journal = self.addJournal()
        post = self.addPost()

        self.assertSequenceEqual(journal.posts, [post])
        self.assertSequenceEqual(journal.keys(), [1])
        self.assertSequenceEqual(journal.values(), [post])
        self.assertSequenceEqual(journal.items(), [(1, post)])

    def test_post_delete(self):
        journal = self.addJournal()
        post = self.addPost()

        del journal[1]

        self.assertSequenceEqual(journal.keys(), [])
        self.assertEqual(DBSession.query(Post).count(), 0)

    def test_journal_add_post_by_attributes(self):
        journal = self.addJournal()
        post = self.addPost()

        post2 = journal.add_post(title='Foo', _flush=True)

        self.assertEquals(len(journal.posts), 2)
        self.assertSequenceEqual(journal.keys(), [1, 2])
        self.assertSequenceEqual(journal.values(), [post, post2])

    def test_journal_add_post_by_object(self):
        journal = self.addJournal()
        post = self.addPost()

        post2 = Post(title='Foo')
        journal.add_post(post2)

        self.assertEquals(len(journal.posts), 2)
        self.assertSequenceEqual(journal.keys(), [1, 2])
        self.assertSequenceEqual(journal.values(), [post, post2])


class PostModelTest(ModelBaseTest):
    def test_post(self):
        journal = self.addJournal()
        post = self.addPost()

        self.assertEqual(post.journal_name, 'distractionbike')
        self.assertEqual(post.title, 'First Post')
        self.assertEqual(post.lede, 'First lede')
        self.assertEqual(post.journal.name, 'distractionbike')
        self.assertEqual(len(post.comments), 0)

    def test_post_traversal(self):
        journal = self.addJournal()
        post = self.addPost()

        self.assertEqual(post.__name__, '1')
        self.assertEqual(post.__parent__, journal)

    def test_acl(self):
        journal = self.addJournal()
        post = self.addPost()

        self.assertSequenceEqual(
            post.__acl__,
            [(Allow, Everyone, 'view'),
             (Allow, Authenticated, 'add'),
             (Allow, 'group:editors', ('edit', 'add', 'delete')),
             (Allow, 'distractionbike', ('edit', 'add', 'delete')),
            ])

    def test_post_404(self):
        journal = self.addJournal()
        post = self.addPost()
        self.assertRaises(KeyError, lambda: journal[999])

    def test_post_del(self):
        journal = self.addJournal()
        post = self.addPost()

        post.delete()

        self.assertSequenceEqual(journal.keys(), [])
        self.assertEqual(DBSession.query(Post).count(), 0)

    def test_post_add_comment_by_attributes(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()

        self.assertEquals(len(post.comments), 1)
        comment2 = post.add_comment(text='Foo', user_id='bob', _flush=True)

        self.assertEquals(DBSession.query(Comment).count(), 2)
        self.assertEquals(len(post.comments), 2)
        self.assertSequenceEqual(post.keys(), [1, 2])
        self.assertSequenceEqual(post.values(), [comment, comment2])
        self.assertSequenceEqual(post.items(),
                                 [(1, comment), (2, comment2)])

    def test_post_add_comment_by_object(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()

        self.assertEquals(len(post.comments), 1)
        comment2 = Comment(text='Foo', user_id='bob')
        post.add_comment(comment2, _flush=True)

        self.assertEquals(DBSession.query(Comment).count(), 2)
        self.assertEquals(len(post.comments), 2)
        self.assertSequenceEqual(post.keys(), [1, 2])
        self.assertEquals(post.values(), [comment, comment2])
        self.assertSequenceEqual(post.items(),
                                 [(1, comment), (2, comment2)])


    def test_post_del_comment(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()

        del post[1]
        self.assertEquals(len(post.comments), 0)
        self.assertSequenceEqual(post.keys(), [])


class CommentModelTest(ModelBaseTest):
    def test_comment(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()

        self.assertEqual(comment.user_id, 'bob')
        self.assertEqual(comment.text, 'First Comment')
        self.assertEqual(comment.hidden, False)
        self.assertEqual(comment.post.id, 1)

    def test_comment_traversal(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()

        self.assertEqual(comment.__name__, '1')
        self.assertEqual(comment.__parent__, post)

    def test_acl(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()

        self.assertSequenceEqual(
            comment.__acl__,
            [(Allow, Everyone, 'view'),
             (Allow, Authenticated, 'add'),
             (Deny, Everyone, ('add', 'edit', 'delete')),
             (Allow, 'group:editors', ('edit', 'delete', 'publish', 'hide')),
             (Allow, 'distractionbike', ('publish', 'hide')),
            ])

    def test_comment_404(self):
        journal = self.addJournal()
        post = self.addPost()
        comment = self.addComment()

        self.assertRaises(KeyError, lambda: post[999])


class UserModelTest(ModelBaseTest):
    def test_user(self):
        user = self.addUser()

        self.assertEqual(user.name, 'distractionbike')
        self.assertTrue(user.verifyPassword('secret'))
        self.assertEqual(user.password_md5, '5ebe2294ecd0e0f08eab7690d2a6ee69')

