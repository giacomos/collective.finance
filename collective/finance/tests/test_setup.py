# -*- coding: utf-8 -*-
import unittest2 as unittest

from collective.finance.testing import \
    COLLECTIVE_FINANCE_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles


class CollectiveFinanceSetupTest(unittest.TestCase):

    layer = COLLECTIVE_FINANCE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.types = self.portal.portal_types

    def test_browserlayer_available(self):
        from plone.browserlayer import utils
        from collective.finance.interfaces import \
            IFinanceLayer
        self.assertTrue(
            IFinanceLayer in utils.registered_layers()
        )


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
