"""OkArchive tests."""

import transaction

from pyramid.security import (
    Allow,
    Everyone,
    )

from ..models import DBSession



class AllAllowedRootFactory:
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Everyone, 'add'),
        (Allow, Everyone, 'edit'),
        (Allow, Everyone, 'delete'),
    ]


resource = AllAllowedRootFactory()


def _initTestingDB():
    import hashlib
    from sqlalchemy import create_engine
    from okarchive.models import (
        Base,
        Journal,
        Post,
        Comment,
        User,
        )

    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)

    with transaction.manager:
        md5 = hashlib.md5('secret'.encode()).hexdigest()
        user = User(name='distractionbike', password_md5=md5)
        DBSession.add(user)
        journal = Journal(name='distractionbike')
        DBSession.add(journal)
        post = Post(
            journal_name='distractionbike',
            title='First Post',
            lede='First lede',
            text='<b>My body</b>')
        DBSession.add(post)
        DBSession.flush()
        comment = Comment(post_id=post.id, user_id='bob', text='First Comment')
        DBSession.add(comment)

    return DBSession


#from . import models
#from . import security
#from . import views
#from . import functional