from pyramid.security import (
    principals_allowed_by_permission as pabp,
    Everyone
)

from okarchive.tests import BaseDatabaseTest, DBSession
from okarchive.security import (
    authenticate,
    group_finder,
)

class TestSecurity(BaseDatabaseTest):

    def test_authenticate(self):
        self.addUser()

        self.assertTrue(authenticate('distractionbike', 'secret'))

    def test_groups(self):
        self.assertSequenceEqual(group_finder('distractionbike',
                                              request=None),
                                 ['group:editors'])

    def test_journal_security(self):
        journal = self.addJournal()

        self.assertSequenceEqual(pabp(journal, 'view'), [Everyone])
        # FIXME: these should not work!
        # To do this, we need an integration test!
        self.assertSequenceEqual(pabp(journal, 'add'), [Everyone])
        self.assertSequenceEqual(pabp(journal, 'edit'), [Everyone])
        self.assertSequenceEqual(pabp(journal, 'delete'), [Everyone])

