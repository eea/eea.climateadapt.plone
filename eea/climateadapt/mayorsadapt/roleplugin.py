""" A PAS plugin to facilitate editing content by City Mayors """

from AccessControl import ClassSecurityInfo
from AccessControl.users import BasicUser
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from Products.PluggableAuthService.interfaces.plugins import IAnonymousUserFactoryPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope.interface import implements
from eea.climateadapt.city_profile import TOKENID


# Monkeypatch _isTop() to be able to create special Anonymous City Mayor users.
# PAS is such built that it only builds anonymous users in the top acl_users.
# We want to be able to build them from the Plone site level.
from Products.PluggableAuthService.PluggableAuthService import PluggableAuthService


def is_citymayor_visitor(request):
    """ Is this browsing session belong to a city mayor visitor?
    """

    if request.cookies.get(TOKENID):    # or request.SESSION.get(TOKENID): #Session Problems
        return True

    return False


_old_isTop = PluggableAuthService._isTop


def _new_isTop(self):
    if is_citymayor_visitor(self.REQUEST):
        return True
    return _old_isTop(self)

PluggableAuthService._isTop = _new_isTop


def manage_addCityMayorUserFactory(dispatcher, id, title=None, RESPONSE=None):
    """
    add a local roles manager
    """
    rm = CityMayorUserFactory(id, title)
    dispatcher._setObject(rm.getId(), rm)

    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')

manage_addCityMayorUserFactoryForm = DTMLFile('./CityMayorUserFactoryForm',
                                                globals())


CITYMAYOR = 'CityMayor'


class CityMayorUser(BasicUser):
    """ An almost Anonymous User with a fixed username: CityMayor """

    def __init__(self):
        self.name = CITYMAYOR

    def getUserName(self):
        """Get the name used by the user to log into the system.
        """
        return self.name

    def getRoles(self):
        """Get a sequence of the global roles assigned to the user.
        """
        return ('CityMayor', )

    def getDomains(self):
        """Get a sequence of the domain restrictions for the user.
        """
        return ()


class CityMayorUserFactory(BasePlugin):
    """ A user factory that uses CityMayorUser as its users

    These users are transient principals, they're not stored in the database.

    With the help of _new_isTop, these users are generated only for specially
    marked requests (checking presence of special access token), so it doesn't
    interfere for the rest of the site.

    The CityProfile model class has a special implementation of
    __ac_local_roles__ that can authenticate the token against that CityProfile
    and grant this anonymous user the Owner role.

    Then the rest of the permissions problem is solved with the help of
    workflow.

    The CityMayor role is used to allow adding content to the /city-profile
    folder.

    This plugin also implements enumerateUsers, to be able to provide
    information on the CityMayor user
    """

    meta_type = "CityMayor User Factory"
    security = ClassSecurityInfo()

    implements(IAnonymousUserFactoryPlugin, IUserEnumerationPlugin)

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title

    def createAnonymousUser(self):
        self.REQUEST.set('disable_border', True)
        return CityMayorUser()

    def enumerateUsers(self, **kw):
        if kw['id'] == CITYMAYOR:
            info = {'id': CITYMAYOR,
                    'login': CITYMAYOR,
                    'pluginid': self.getId(),
                    }
            return (info,)

InitializeClass(CityMayorUserFactory)
