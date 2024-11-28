from zope.interface import implementer
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


@implementer(IResetTokenEvent)
class ResetTokenEvent(ObjectEvent):
    """"""


@implementer(ITokenAboutToExpireEvent)
class TokenAboutToExpireEvent(ObjectEvent):
    """"""

@implementer(ITokenExpiredEvent)
class TokenExpiredEvent(ObjectEvent):
    """"""


@implementer(ICityProfileRegisterEvent)
class CityProfileRegisterEvent(ObjectEvent):
    """"""


def mayor_logout(event):
    request = event.object.REQUEST
    request.response.expireCookie(TOKEN_COOKIE_NAME)
