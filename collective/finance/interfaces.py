from zope.interface import Interface
from plone.namedfile.field import NamedFile
from collective.finance import messageFactory as _


class IFinanceLayer(Interface):
    """Marker interface that defines a ZTK browser layer. We can reference
    this in the 'layer' attribute of ZCML <browser:* /> directives to ensure
    the relevant registration only takes effect when this theme is installed.

    The browser layer is installed via the browserlayer.xml GenericSetup
    import step.
    """


class IFinanceWallet(Interface):
    """
    """


class IFinanceAccount(Interface):
    """
    """


class IFinanceTransfer(Interface):
    """
    """


class IFinanceTransaction(Interface):
    """
    """


class IImportQIFFormSchema(Interface):
    """ Define fields used on the form """

    qif_file = NamedFile(title=_(u"QIF file"))


class IQIFParser(Interface):

    def parseQIFdata(data):
        """
        """
