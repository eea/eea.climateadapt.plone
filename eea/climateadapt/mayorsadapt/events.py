from zope.interface import Interface, implements
from zope.component.interfaces import ObjectEvent, IObjectEvent
from plone.app.contentrules.handlers import execute_rules


class IResetTokenEvent(IObjectEvent):
    """ The access token has been reset
    """


class ITokenAboutToExpireEvent(IObjectEvent):
    """ The access token is about to expire (in a certain time)
    """


class ITokenExpiredEvent(IObjectEvent):
    """ The access token has expired
    """


class ResetTokenEvent(ObjectEvent):
    implements(IResetTokenEvent)


class TokenAboutToExpireEvent(ObjectEvent):
    implements(ITokenAboutToExpireEvent)


class TokenExpiredEvent(ObjectEvent):
    implements(ITokenExpiredEvent)


def trigger_contentrules(event):
    execute_rules(event)
