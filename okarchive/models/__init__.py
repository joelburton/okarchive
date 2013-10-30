"""
Models for OkArchive journals.

These classes are for the journals, posts, and comments on the posts.
They will be persisted in SQLAlchemy.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import Allow, Everyone


DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()


def RootFactory(request):
    """Return site root."""

    return siteRoot


class SiteRoot:
    """Site root for OkArchive.

    A simple resource that has the journals object in its
    mapping.
    """

    __name__ = ''
    __parent__ = None
    __acl__ = [(Allow, Everyone, 'view')]

    def __getitem__(self, item):
        """Return items in root; only journals."""

        return {'journals': journals}[item]


siteRoot = SiteRoot()


from .user import User
from .journal import Journal
from .journals import Journals, journals
from .post import Post
from .comment import Comment

