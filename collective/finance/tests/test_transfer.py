# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone.app.testing import TEST_USER_ID, setRoles
from collective.finance.testing import \
    COLLECTIVE_FINANCE_INTEGRATION_TESTING
from collective.finance.interfaces import IFinanceTransfer
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
        self.portal.invokeFactory(
            'FinanceWallet',
            'test-wallet'
        )
        self.wallet = self.portal['test-wallet']
        self.wallet.invokeFactory(
            'FinanceAccount',
            'test-account'
        )

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='FinanceTransfer')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_FinanceTransfer')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='FinanceTransfer'
        )
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='FinanceTransfer'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IFinanceTransfer.providedBy(new_object))

    def test_adding(self):
        self.wallet.invokeFactory(
            'FinanceTransfer',
            'transfer1'
        )
        self.assertTrue(IFinanceTransfer.providedBy(self.wallet['transfer1']))
