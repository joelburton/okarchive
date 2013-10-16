from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    ForeignKey,
    DateTime,
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

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Journal(Base):
    __tablename__ = 'journals'
    name = Column(String, primary_key=True)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    journal_name = Column(String, ForeignKey('journals.name',
                                             ondelete='CASCADE',
                                             onupdate='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    text = Column(Text)
    creation_date = Column(DateTime, server_default=func.now())

    journal = relationship("Journal",
                           backref=backref('posts',
                                           order_by=id,
                                           cascade='all, delete-orphan',
                                           passive_deletes=True))


Index('post_journalname', Post.journal_name)
Index('post_title', Post.title)