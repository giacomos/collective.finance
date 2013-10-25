import ccy
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
        wallet = context.get_wallet()
        path = '/'.join(wallet.getPhysicalPath())
        if catalog is None:
            return SimpleVocabulary([])
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

AccountsVocabularyFactory = CatalogVocabularyFactory('finance-account')
TransactionsVocabularyFactory = CatalogVocabularyFactory('transaction')
TransfersVocabularyFactory = CatalogVocabularyFactory('transfer')
CurrenciesVocabularyFactory = SimpleVocabularyFactory({ccy.currency(c).code: ccy.currency(c).name for c in ccy.all()})
