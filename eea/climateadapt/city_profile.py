from plone.directives import dexterity, form
from zope.interface import implements


class ICityProfile(form.Schema):
    """
    Defines content-type schema for CityProfile
    """


class CityProfile(dexterity.Container):
    implements(ICityProfile)

    search_type = "CITYPROFILE"
    secret = "zzz"

    def __ac_local_roles__(self):
        tk = self.REQUEST.SESSION.get('tk')
        if tk == self.secret:
            #print "returning city mayor role", self.REQUEST['ACTUAL_URL']
            return {'CityMayor': ['CityMayor']}
        return {}
