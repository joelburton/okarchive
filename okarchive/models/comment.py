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

from pyramid.security import (
    Allow,
    Deny,
    Everyone,
    Authenticated,
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

    @property
    def __acl__(self):
        """Permissions."""

        return [(Allow, Everyone, 'view'),
                (Allow, Authenticated, 'add'),
                (Deny, Everyone, ('add', 'edit', 'delete')),
                (Allow, 'group:editors', ('edit', 'delete', 'publish', 'hide')),
                (Allow, self.post.journal_name, ('publish', 'hide')),
        ]

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
        server_onupdate=func.now(),
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