import unittest

from . import _initTestingDB, DBSession


class TestSecurity(unittest.TestCase):
    def setUp(self):
        _initTestingDB()

    def tearDown(self):
        DBSession.remove()

    def test_authenticate(self):
        from ..security import authenticate

        self.assertTrue(authenticate('distractionbike', 'secret'))

    def test_groups(self):
        from ..security import group_finder

        self.assertSequenceEqual(group_finder('distractionbike',
                                              request=None),
                                 ['group:editors'])

