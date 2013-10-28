"""Security code."""

import logging

USERS = {'joel': 'joelpass',
         'bob': 'bobpass',
}

GROUPS = {'joel': ['group:editors'],
}

log = logging.getLogger(__name__)


def group_finder(userid, request):
    """Given a userid, return groups they are part of."""

    log.debug('groupfinder: %s', userid)
    if userid in USERS:
        return GROUPS.get(userid, [])