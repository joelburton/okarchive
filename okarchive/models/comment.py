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
from sqlalchemy.orm import (
    relationship,
    backref,
    )

from . import Base, DBSession


class Comment(Base):
    """Comment."""

    __tablename__ = 'comments'

    @property
    def __name__(self):
        return str(self.id)

    @property
    def __parent__(self):
        return self.post


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