from zope.interface import implements
from zope.component.interfaces import ObjectEvent, IObjectEvent
from eea.climateadapt.city_profile import TOKEN_COOKIE_NAME


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


def mayor_logout(event):
    request = event.object.REQUEST
    request.response.expireCookie(TOKEN_COOKIE_NAME)
