import os
import sys
import hashlib

import transaction
from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Base,
    Journal,
    Post,
    User,
    )


def usage(argv): #pragma NOCOVER
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv): #pragma NOCOVER

    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    with transaction.manager:
        password = hashlib.md5('secret'.encode()).hexdigest()
        user = User(name='distractionbike', password_md5=password)
        DBSession.add(user)
        journal = Journal(name='distractionbike')
        DBSession.add(journal)
        post = Post(journal_name='distractionbike', title='First Post')
        DBSession.add(post)
