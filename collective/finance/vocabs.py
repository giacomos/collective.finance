from money import CURRENCY
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from collective.finance import messageFactory as _


class CatalogVocabularyFactory(object):

    implements(IVocabularyFactory)

    portal_type = None

    def __init__(self, pt):
        self.portal_type = pt

    def __call__(self, context):
        if not self.portal_type:
            return SimpleVocabulary([])

        catalog = getToolByName(context, "portal_catalog", None)
        if catalog is None or not hasattr(context, 'get_wallet'):
            return SimpleVocabulary([])
        wallet = context.get_wallet()
        path = '/'.join(wallet.getPhysicalPath())
        terms = []
        brains = catalog.searchResults(portal_type=self.portal_type,
                                       path=path)

        terms = [SimpleTerm(title=_(brain.Title), value=brain.UID)
                 for brain in brains]
        return SimpleVocabulary(sorted(terms, key=lambda elem: elem.title))


class SimpleVocabularyFactory(object):
    implements(IVocabularyFactory)

    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, context):
        terms = [SimpleTerm(title=_(title), value=value)
                 for value, title in self.vocab.iteritems()]
        return SimpleVocabulary(sorted(terms, key=lambda elem: elem.title))

AccountsVocabularyFactory = CatalogVocabularyFactory('FinanceAccount')
TransactionsVocabularyFactory = CatalogVocabularyFactory('FinanceTransaction')
CategoriesVocabularyFactory = CatalogVocabularyFactory('FinanceCategory')
TransfersVocabularyFactory = CatalogVocabularyFactory('FinanceTransfer')
currency_vocab = {v.code: v.name for k, v in CURRENCY.iteritems()}
CurrenciesVocabularyFactory = SimpleVocabularyFactory(currency_vocab)


account_types = {
    'Cash': 'Cash',
    'Bank': 'Bank',
    'CCard': 'Credit Card',
    'Invst': 'Investing',
    'Oth A': 'Asset',
    'Oth L': 'Liability',
}

AccountTypesVocabularyFactory = SimpleVocabularyFactory(currency_vocab)
