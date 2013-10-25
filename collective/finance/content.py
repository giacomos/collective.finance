from plone.directives import form
from plone.dexterity.content import Item
from plone.dexterity.content import Container
from zope.interface import implements

from collective.finance.interfaces import IWallet
from collective.finance.interfaces import IAccount
from collective.finance.interfaces import ITransaction
from collective.finance.interfaces import ITransfer


class Wallet(Container):
    '''
    Applicazione class
    '''
    implements(IWallet)

    def get_wallet(self):
        return self.aq_inner

class Transaction(Item):
    '''
    Applicazione class
    '''
    implements(ITransaction)

class Transfer(Item):
    '''
    Applicazione class
    '''
    implements(ITransfer)


class Account(Item):
    '''
    Applicazione class
    '''
    implements(IAccount)
