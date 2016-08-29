from zope.interface import implements
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


class ICityProfileRegisterEvent(IObjectEvent):
    """ A new city profile registration
    """


class ResetTokenEvent(ObjectEvent):
    implements(IResetTokenEvent)


class TokenAboutToExpireEvent(ObjectEvent):
    implements(ITokenAboutToExpireEvent)


class TokenExpiredEvent(ObjectEvent):
    implements(ITokenExpiredEvent)


class CityProfileRegisterEvent(ObjectEvent):
    implements(ICityProfileRegisterEvent)


def trigger_contentrules(event):
    execute_rules(event)
