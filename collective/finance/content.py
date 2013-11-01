from plone.dexterity.content import Item
from plone.dexterity.content import Container
from zope.interface import implements

from collective.finance.interfaces import (
    IFinanceWallet,
    IFinanceAccount,
    IFinanceTransaction,
    IFinanceTransfer,
    IFinanceCategory,
    IFinanceAmountSplit
)


class FinanceWallet(Container):
    '''
    Applicazione class
    '''
    implements(IFinanceWallet)

    def get_wallet(self):
        return self.aq_inner


class FinanceTransaction(Container):
    '''
    Applicazione class
    '''
    implements(IFinanceTransaction)


class FinanceAmountSplit(Item):
    '''
    Applicazione class
    '''
    implements(IFinanceAmountSplit)


class FinanceTransfer(Item):
    '''
    Applicazione class
    '''
    implements(IFinanceTransfer)


class FinanceAccount(Container):
    '''
    Applicazione class
    '''
    implements(IFinanceAccount)


class FinanceCategory(Item):
    '''
    Applicazione class
    '''
    implements(IFinanceCategory)
