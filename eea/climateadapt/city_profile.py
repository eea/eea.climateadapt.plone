from plone.directives import dexterity, form
from zope.globalrequest import getRequest
from zope.interface import implements, Interface


class ICityProfile(form.Schema):
    """
    Defines content-type schema for CityProfile
    """


class ICityProfileStaging(Interface):
    """ A marker interface for CityProfiles.

    It is needed because behaviors (such as IStagingBehavior) are applied as
    marker interfaces to the object and such are more concrete when trying to
    lookup a view on CityProfiles. Basically, it is needed to be able to
    reimplement the @@iterate-control as an override view
    """


class CityProfile(dexterity.Container):
    implements(ICityProfile)

    search_type = "CITYPROFILE"
    secret = "zzz"

    @property
    def __ac_local_roles__(self):
        req = getRequest()
        tk = req.SESSION.get('tk')
        #import pdb; pdb.set_trace()
        if tk == self.secret:
            return {'CityMayor': ['Owner',]}
        return {}
