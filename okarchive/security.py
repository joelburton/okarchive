USERS = {'joel': 'joelpass',
         'bob': 'bobpass'}
GROUPS = {'joel': ['group:editors']}

import logging

log = logging.getLogger(__name__)

def groupfinder(userid, request):
    log.info('groupfinder: %s', userid)
    if userid in USERS:
        return GROUPS.get(userid, [])