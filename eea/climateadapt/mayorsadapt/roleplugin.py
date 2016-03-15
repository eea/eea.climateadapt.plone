""" A plone PAS plugin to assign a role based on a token """


from AccessControl import ClassSecurityInfo
from AccessControl.users import BasicUser
from Acquisition import aq_inner, aq_parent
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from Products.PluggableAuthService.interfaces.plugins import IAnonymousUserFactoryPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope.interface import implements


def manage_addTokenBasedRolesManager(dispatcher, id, title=None, RESPONSE=None):
    """
    add a local roles manager
    """
    rm = TokenBasedRolesManager(id, title)
    dispatcher._setObject(rm.getId(), rm)

    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')

manage_addTokenBasedRolesManagerForm = DTMLFile('./TokenBasedRolesManagerForm',
                                                globals())


class CityMayorUser(BasicUser):
    """A very simple user implementation

    that doesn't make a database commitment"""

    def __init__(self): #, name, password, roles, domains):
        self.name = 'Anonymous'
        #self.roles = ('Anonymous',)    #'CityMayor', 'Authenticated')
        self.roles = ('CityMayor',)

    def getUserName(self):
        """Get the name used by the user to log into the system.
        """
        return self.name

    def getRoles(self):
        """Get a sequence of the global roles assigned to the user.
        """
        return self.roles

    def getDomains(self):
        """Get a sequence of the domain restrictions for the user.
        """
        return ()

    def getId(self):
        return None


class TokenBasedRolesManager(BasePlugin):
    """ Token role manager
    """

    meta_type = "TokenBased Roles Manager"
    security = ClassSecurityInfo()

    implements(IAnonymousUserFactoryPlugin)

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title

    def createAnonymousUser(self):
        user = CityMayorUser()  #'City Mayor', '', ('CityMayor', ), [])
        print "create CityMayor user", user
        return user


InitializeClass(TokenBasedRolesManager)
