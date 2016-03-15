from plone.directives import dexterity, form
from zope.interface import implements


class ICityProfile(form.Schema):
    """
    Defines content-type schema for Ace Item
    """
    #form.model("city_profile.xml")


class CityProfile(dexterity.Container):
    implements(ICityProfile)

    search_type = "CITYPROFILE"
    secret = "zzz"

    def __ac_local_roles__(self):
        if self.REQUEST.get('mk') == self.secret:
            return {'CityMayor': ['CityMayor']}
        return {}
