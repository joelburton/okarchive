"""Security code."""

import logging

from .models import (
    DBSession,
    User,
)

GROUPS = {'distractionbike': ['group:editors'],
}

log = logging.getLogger(__name__)


def group_finder(userid, request):
    """Given a userid, return groups they are part of."""

    log.debug('groupfinder: %s', userid)
    return GROUPS.get(userid, [])


def authenticate(userid, password):
    """Authenticate user."""

    log.debug('authenticate: %s, %s', userid, password)
    user = (DBSession
            .query(User)
            .filter(User.name == userid)
            .first())
    if user:
        return user.verifyPassword(password)