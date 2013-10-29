# -*- coding: utf-8 -*-
import os
import unittest2 as unittest
from collective.finance.testing import \
    COLLECTIVE_FINANCE_INTEGRATION_TESTING


class QIFParserUtilityIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_FINANCE_INTEGRATION_TESTING

    def test_getutility(self):
        from zope.component import getUtility
        from collective.finance.interfaces import IQIFParser
        ut = getUtility(IQIFParser, name='collective.finance.qifparser')
        self.failUnless(ut)

    def test_parsing(self):
        from zope.component import getUtility
        from collective.finance.interfaces import IQIFParser
        ut = getUtility(IQIFParser, name='collective.finance.qifparser')
        filename = os.path.join(os.path.dirname(__file__), u'file.qif')
        f = open(filename)
        struct = ut.parseQIFdata(f.read())
        self.failUnless(len(struct['transactions']) > 0)
