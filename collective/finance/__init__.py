from zope.i18n import MessageFactory

messageFactory = MessageFactory("collective.finance")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
