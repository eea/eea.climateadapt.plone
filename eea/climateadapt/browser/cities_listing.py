import os
from zope.interface import Interface
from zope.interface import implements
from plone.app.contenttypes.browser.folder import FolderView


class ICitiesProfilesView(Interface):
    """ City Profiles Interface """


class CitiesProfilesView(FolderView):
    """ Custom view for  city-profiles"""

    implements(ICitiesProfilesView)
