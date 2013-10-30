"""OkArchive tests."""

import hashlib
import unittest

from sqlalchemy import create_engine

from okarchive.models import (
    Base,
    Journal,
    Post,
    Comment,
    User,
    DBSession,
    )

class BaseDatabaseTest(unittest.TestCase):

    def setUp(self):
        self.setUpDb()

    def tearDown(self):
        DBSession.remove()

    def setUpDb(self):
        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        DBSession.configure(bind=engine)

    def addUser(self):
        if not (DBSession
                .query(User)
                .filter(User.name == 'distractionbike')
                .first()):
            md5 = hashlib.md5('secret'.encode()).hexdigest()
            user = User(name='distractionbike', password_md5=md5)
            DBSession.add(user)
            return user

    def addJournal(self):
        journal = Journal(name='distractionbike')
        DBSession.add(journal)
        return journal

    def addPost(self):
        post = Post(
            journal_name='distractionbike',
            title='First Post',
            lede='First lede',
            text='<b>My body</b>')
        DBSession.add(post)
        DBSession.flush()
        return post

    def addComment(self):
        comment = Comment(post_id=1, user_id='bob', text='First Comment')
        DBSession.add(comment)
        DBSession.flush()
        return comment

    def addAll(self):
        self.addUser()
        self.addJournal()
        self.addPost()
        self.addComment()