from sqlalchemy import (
    Column,
    String,
)

from pyramid.security import Allow, Everyone

from . import Base, DBSession
from .post import Post

class Journal(Base):
    """Journal."""

    __tablename__ = 'journals'

    @property
    def __name__(self):
        return self.name

    @property
    def __parent__(self):
        from .journals import journals
        return journals

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

    def __delitem__(self, key):
        """Delete post."""

        self.posts.remove(self[key])

    def values(self):
        """List of posts."""

        return [p for p in self.posts]

    def keys(self):
        """List of post IDs."""

        return [p.id for p in self.posts]

    def items(self):
        """List of (journal-name, journal) tuples."""

        return [(p.id, p) for p in self.posts]


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


