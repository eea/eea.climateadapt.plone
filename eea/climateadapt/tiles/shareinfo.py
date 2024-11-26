""" A view that can be embeded in a tile.

It renders a search "portlet" for Ace content
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt.config import DEFAULT_LOCATIONS
from eea.climateadapt.vocabulary import _cca_types
from plone import api
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements

from eea.climateadapt.translation.utils import TranslationUtilsMixin


class IShareInfoTile(IPersistentCoverTile):

    title = schema.TextLine(
        title='Title',
        required=False,
    )

    shareinfo_type = schema.Choice(
        title="Share info type",
        vocabulary="eea.climateadapt.cca_types",
        required=False
    )


class ShareInfoTile(PersistentCoverTile, TranslationUtilsMixin):
    """ Share info tile

    It shows a button with link to creating content of a certain type
    """

    implements(IShareInfoTile)

    index = ViewPageTemplateFile('pt/shareinfo.pt')

    is_configurable = True
    is_editable = True
    is_droppable = False
    short_name = 'Share info'

    def is_anon(self):
        return api.user.is_anonymous()

    def is_empty(self):
        return False

    def link_url(self):
        site = getSite()    # TODO: fix this link
        type_ = self.data.get('shareinfo_type')
        location, _t, factory = DEFAULT_LOCATIONS[type_]
        location = self.current_lang + '/' + location
        location = site.restrictedTraverse(location)
        url = location.absolute_url().replace("/"+self.current_lang+"/", "/en/")
        return "{0}/++add++{1}".format(url, factory)

    def link_title(self):
        type_ = self.data.get('shareinfo_type')
        label = dict(_cca_types)[type_]
        return "Add a {0}".format(label)
