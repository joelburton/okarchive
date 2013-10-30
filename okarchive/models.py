"""
Models for OkArchive journals.

These classes are for the journals, posts, and comments on the posts.
They will be persisted in SQLAlchemy.
"""

import hashlib

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    func,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

from zope.sqlalchemy import ZopeTransactionExtension

import deform
import colander

from pyramid.security import (
    Allow,
    Everyone,
    )


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    """System user."""

    __tablename__ = 'users'

    name = Column(
        String,
        primary_key=True,
    )
    password_md5 = Column(
        String,
        nullable=False,
    )

    def verifyPassword(self, password):
        """Verify password."""

        md5 = hashlib.md5(password.encode()).hexdigest()
        return md5 == self.password_md5


def RootFactory(request):
    return siteRoot


class SiteRoot:
    __name__ = ''
    __parent__ = None
    __acl__ = [(Allow, Everyone, 'view')]

    def __getitem__(self, item):
        return {'journals': journals}[item]

siteRoot = SiteRoot()


class Journals:
    """Traversable container for journals."""

    __name__ = 'journals'
    __parent__ = siteRoot

    def __getitem__(self, item):
        """Get journal by name."""

        journal = (DBSession
                .query(Journal)
                .filter(Journal.name == item)
                .first())
        if not journal:
            raise KeyError('No such journal: {}'.format(item))
        return journal

    def __setitem__(self, key, value):
        """Add a journal."""

        raise NotImplementedError("Can't add journal")

    def __delitem__(self, key):
        """Delete a journal."""

        raise NotImplementedError("Can't delete journal")

    def values(self):
        """List of journals."""

        return [j for j in self.journals]

    def keys(self):
        """List of journal names."""

        return [ j.name for j in self.journals ]

    def items(self):
        """List of (journal-name, journal) tuples."""

        return [(j.name, j) for j in self.journals ]

    @property
    def journals(self):
        """Return list of journals."""

        # XXX: do we need to worry about getting journals without a sort order?
        return (DBSession
                .query(Journal)
                .order_by(Journal.name)
        )

journals = Journals()


class Journal(Base):
    """Journal."""

    __tablename__ = 'journals'

    @property
    def __name__(self):
        return self.name

    __parent__ = journals

    @property
    def __acl__(self):
        """Permisssions."""

        return [(Allow, Everyone, 'view'),
                (Allow, 'group:editors', ('edit', 'add', 'delete')),
                (Allow, self.name, ('edit', 'add', 'delete')),
        ]

    def __getitem__(self, item):
        """Get post by id."""

        post = (DBSession
                .query(Post)
                .filter(Post.id == item)
                .filter(Post.journal_name == self.name)
                .first())
        if not post:
            raise KeyError('No such post: {}'.format(item))
        return post

    def __setitem__(self, key, post):
        """Set post in journal.

        This should be uncommonly called; normally call add_post, since
        that doesn't require that we know the post id in advance--they're
        auto-incremented by the database. This might be useful if we need
        to replace a post with a new one with a pre-used number.
        """

        if post.journal_name != self.name:
            raise ValueError('Post journal.name does not match journal: {}, {}'
                    .format(post.journal_name, self.name))
        self.posts.append(post)
        DBSession.flush()    # we'll want the auto-inc'd post ID

    def __delitem__(self, key):
        """Delete post."""

        self.posts.remove(self[key])

    name = Column(
        String,
        primary_key=True,
    )

    def add_post(self,
                 post=None,
                 _flush=False,
                 **kw
                 ):
        if not post:
            post = Post(journal_name=self.name, **kw)
        else:
            post.journal_name = self.name
        DBSession.add(post)
        if _flush:
            DBSession.flush()
        return post

    def values(self):
        """List of posts."""

        return [p for p in self.posts]

    def keys(self):
        """List of post IDs."""

        return [p.id for p in self.posts]

    def items(self):
        """List of (journal-name, journal) tuples."""

        return [(p.id, p) for p in self.posts]


class Post(Base):
    """Post."""

    __tablename__ = 'posts'

    @property
    def __name__(self):
        return str(self.id)

    @property
    def __parent__(self):
        return self.journal

    @property
    def __acl__(self):
        """Permissions."""

        return [(Allow, Everyone, 'view'),
                (Allow, 'group:editors', ('edit', 'add', 'delete')),
                (Allow, self.name, ('edit', 'add', 'delete')),
        ]

    id = Column(
        Integer,
        primary_key=True,
    )
    journal_name = Column(
        String,
        ForeignKey('journals.name',
                   ondelete='CASCADE',
                   onupdate='CASCADE'),
        nullable=False,
    )
    title = Column(
        String,
        nullable=False,
        info={'colanderalchemy':
                  dict(title='Title',
                       default='',
                       validator=colander.Length(1, 50),
                       widget=deform.widget.TextInputWidget(),
                  )},
    )
    lede = Column(
        Text,
        nullable=True,
        info={'colanderalchemy':
                  dict(title='Lead In',
                       default='',
                       validator=colander.Length(0,400),
                       widget=deform.widget.TextAreaWidget(),
                    )}
    )
    text = Column(
        Text,
        info={'colanderalchemy':
                  dict(widget=deform.widget.RichTextWidget(),
                       title='Body Text',
                       default='',
                  )},
    )
    creation_date = Column(
        DateTime,
        server_default=func.now(),
    )
    modification_date = Column(
        DateTime,
        # TODO: autoupdate
    )
    journal = relationship(
        'Journal',
        backref=backref('posts',
                        order_by=id,
                        cascade='all, delete-orphan',
                        passive_deletes=True),
    )

    def delete(self):
        """Delete post."""

        DBSession.delete(self)

    def add_comment(self,
                    comment=None,
                    _flush=False,
                    **kw
    ):

        if not comment:
            comment = Comment(post_id=self.id, **kw)
        else:
            comment.post_id = self.id
        DBSession.add(comment)
        if _flush:
            DBSession.flush()
        return comment


Index('post_journalname', Post.journal_name)
Index('post_title', Post.title)


class Comment(Base):
    """Comment."""

    __tablename__ = 'comments'

    id = Column(
        Integer,
        primary_key=True,
    )
    post_id = Column(
        Integer,
        ForeignKey('posts.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
    )
    user_id = Column(
        String,
        nullable=False,
    ) # FIXME
    text = Column(
        Text,
        nullable=False,
    )
    creation_date = Column(
        DateTime,
        server_default=func.now(),
    )
    modification_date = Column(
        DateTime,
        # TODO: autoupdate
    )
    hidden = Column(
        Boolean,
        default=False,
    )
    post = relationship(
        'Post',
        backref=backref('comments',
                        order_by=id,
                        cascade='all, delete-orphan',
                        passive_deletes=True)
    )



Index('comment_postid', Comment.post_id)