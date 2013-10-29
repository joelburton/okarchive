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


class RootFactory:
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit'),
               (Allow, 'group:editors', 'add'),
               (Allow, 'group:editors', 'delete'),
    ]

    def __init__(self, request):
        pass


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


class Journal(Base):
    """Journal."""

    __tablename__ = 'journals'

    name = Column(
        String,
        primary_key=True,
    )


class Post(Base):
    """Post."""

    __tablename__ = 'posts'

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
    journal = relationship(
        'Journal',
        backref=backref('posts',
                        order_by=id,
                        cascade='all, delete-orphan',
                        passive_deletes=True),
    )


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