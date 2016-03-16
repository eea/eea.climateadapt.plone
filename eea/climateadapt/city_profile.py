from plone.directives import dexterity, form
from zope.globalrequest import getRequest
from zope.interface import implements


class ICityProfile(form.Schema):
    """
    Defines content-type schema for CityProfile
    """


class CityProfile(dexterity.Container):
    implements(ICityProfile)

    search_type = "CITYPROFILE"
    secret = "zzz"

    @property
    def __ac_local_roles__(self):
        req = getRequest()
        tk = req.SESSION.get('tk')
        if tk == self.secret:
            return {'CityMayor': ['Owner',]}
        return {}
