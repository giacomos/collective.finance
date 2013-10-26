from plone.dexterity.content import Item
from plone.dexterity.content import Container
from zope.interface import implements

from collective.finance.interfaces import IFinanceWallet
from collective.finance.interfaces import IFinanceAccount
from collective.finance.interfaces import IFinanceTransaction
from collective.finance.interfaces import IFinanceTransfer


class FinanceWallet(Container):
    '''
    Applicazione class
    '''
    implements(IFinanceWallet)

    def get_wallet(self):
        return self.aq_inner

class FinanceTransaction(Item):
    '''
    Applicazione class
    '''
    implements(IFinanceTransaction)

class FinanceTransfer(Item):
    '''
    Applicazione class
    '''
    implements(IFinanceTransfer)


class FinanceAccount(Item):
    '''
    Applicazione class
    '''
    implements(IFinanceAccount)
