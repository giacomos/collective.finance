# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone.app.testing import TEST_USER_ID, setRoles
from collective.finance.testing import (
    COLLECTIVE_FINANCE_INTEGRATION_TESTING,
    COLLECTIVE_FINANCE_FUNCTIONAL_TESTING
)
from collective.finance.interfaces import IFinanceAccount
from zope.component import (
    getUtility,
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
        self.portal.invokeFactory(
            'FinanceWallet',
            'test-wallet'
        )
        self.wallet = self.portal['test-wallet']

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='FinanceAccount')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_FinanceAccount')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='FinanceAccount'
        )
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='FinanceAccount'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IFinanceAccount.providedBy(new_object))

    def test_adding(self):
        self.wallet.invokeFactory(
            'FinanceAccount',
            'account1'
        )
        self.assertTrue(IFinanceAccount.providedBy(self.wallet['account1']))
