# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone.app.testing import TEST_USER_ID, setRoles
from collective.finance.testing import \
    COLLECTIVE_FINANCE_INTEGRATION_TESTING
from collective.finance.interfaces import IFinanceWallet
from zope.component import (
    queryUtility,
    createObject
)
from plone.dexterity.interfaces import IDexterityFTI


class WalletIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_FINANCE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='FinanceWallet')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_FinanceWallet')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='FinanceWallet'
        )
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='FinanceWallet'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IFinanceWallet.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'FinanceWallet',
            'wallet1'
        )
        self.assertTrue(IFinanceWallet.providedBy(self.portal['wallet1']))
