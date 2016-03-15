""" A plone PAS plugin to assign a role based on a token """


from AccessControl import ClassSecurityInfo
from AccessControl.users import BasicUser
from Acquisition import aq_inner    #, aq_parent
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from Products.PluggableAuthService.interfaces.plugins import IAnonymousUserFactoryPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope.interface import implements

# monkey patch isTop to be able to create special Anonymous users
# PAS is such built that only builds anonymous users in the top acl_users
# we want to be able to build them from the Plone site level
from Products.PluggableAuthService.PluggableAuthService import PluggableAuthService

_old_isTop = PluggableAuthService._isTop
def _new_isTop(self):
    if self.REQUEST.get('mk'):
        # print "ISTOP: ",
        # print self.REQUEST.other['ACTUAL_URL'],
        # print self.REQUEST.other['URL']
        return True
    return _old_isTop(self)

PluggableAuthService._isTop = _new_isTop

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
        self.name = 'CityMayor'
        #self.roles = ('Anonymous',)    #'CityMayor', 'Authenticated')
        #self.roles = ('CityMayor',)

    def getUserName(self):
        """Get the name used by the user to log into the system.
        """
        return self.name

    def getRoles(self):
        """Get a sequence of the global roles assigned to the user.
        """
        print "getRoles"
        return ('Anonymous', )  #self.roles

    def getDomains(self):
        """Get a sequence of the domain restrictions for the user.
        """
        return ()

    def getId(self):
        return self.getUserName()

    def getRolesInContext(self, object):
        # this is not actually used a lot. for example allowed computes
        # local roles by itself. This is stupid.
        print "roles in context", object
        return ('Anonymous', )

    # def allowed(self, object, object_roles=None):
    #     #print "allowed", object, object_roles
    #     if object.getPhysicalPath() == ('', 'Plone', 'about', 'index_html'):
    #         print object.getPhysicalPath(), object_roles
    #         return 1
    #     return 0


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
