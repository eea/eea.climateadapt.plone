from plone.directives import dexterity, form
from zope.interface import implements


class ICityProfile(form.Schema):
    """
    Defines content-type schema for Ace Item
    """


class CityProfile(dexterity.Item):
    implements(ICityProfile)

    search_type = "CITYPROFILE"

    def __ac_local_roles__(self):
        return ()
