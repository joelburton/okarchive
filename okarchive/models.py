from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    ForeignKey,
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
    journal_name = Column(String, ForeignKey('journals.name'), nullable=False)
    title = Column(String, nullable=False)

    journal = relationship("Journal", backref=backref('posts', order_by=id))
