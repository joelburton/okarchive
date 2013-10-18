"""Models for OkArchive journals.

These classes are for the journals, posts, and comments on the posts.
They will be persisted in SQLAlchemy.
"""

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
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass



DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Journal(Base):
    """Journal."""
    __tablename__ = 'journals'
    name = Column(String,
                  primary_key=True,
    )


class Post(Base):
    """Post."""
    __tablename__ = 'posts'
    id = Column(Integer,
                primary_key=True,
    )
    journal_name = Column(String, ForeignKey('journals.name',
                                             ondelete='CASCADE',
                                             onupdate='CASCADE'), nullable=False)
    title = Column(String,
                   nullable=False,
                   info={'colanderalchemy': {'title': 'Title',
                                             'default': '',
                                             'validator': colander.Length(1,50),
                                             'widget': deform.widget.TextInputWidget(
                                                 # "size" param should work, but doesn't
                                                 style='width:30em'
                                             )
                   }},
    )
    text = Column(Text,
                  info={'colanderalchemy': {'widget': deform.widget.RichTextWidget(),
                                            'title': 'Body Text',
                                            'default': ''}},
    )
    creation_date = Column(DateTime,
                           server_default=func.now(),
    )

    journal = relationship("Journal",
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
    id = Column(Integer,
                primary_key=True,
    )
    post_id = Column(Integer,
                     ForeignKey('posts.id', ondelete='CASCADE', onupdate='CASCADE'),
                     nullable=False,
    )
    user_id = Column(String,
                     nullable=False,
    ) # FIXME
    text = Column(Text,
                  nullable=False,
    )
    creation_date = Column(DateTime,
                           server_default=func.now(),
    )
    hidden = Column(Boolean,
                    default=False,
    )

    post = relationship("Post",
                        backref=backref('comments',
                                        order_by=id,
                                        cascade='all, delete-orphan',
                                        passive_deletes=True)
    )


Index('comment_postid', Comment.post_id)