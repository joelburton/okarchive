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
from sqlalchemy.orm import (
    relationship,
    backref,
    )

import deform
import colander

from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    )

from . import Base, DBSession
from .comment import Comment


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
                (Allow, Authenticated, 'add'),
                (Allow, 'group:editors', ('edit', 'add', 'delete')),
                (Allow, self.journal_name, ('edit', 'add', 'delete')),
                ]

    def __getitem__(self, comment_id):
        """Get comment by id."""

        comment = (DBSession
                   .query(Comment)
                   .filter_by(id=comment_id)
                   .first())
        if not comment:
            raise KeyError('No such comment: {}'.format(comment_id))
        return comment

    def __delitem__(self, key):
        """Delete comment."""

        self.comments.remove(self[key])

    def values(self):
        """List of comments."""

        return [c for c in self.comments]

    def keys(self):
        """List of comment IDs."""

        return [c.id for c in self.comments]

    def items(self):
        """List of (comment-id, comment) tuples."""

        return [(c.id, c) for c in self.comments]


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
        default='',
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
        server_onupdate=func.now(),
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
            #DBSession.add(comment)
        self.comments.append(comment)
        if _flush:
            DBSession.flush()
        return comment



Index('post_journalname', Post.journal_name)
Index('post_title', Post.title)
