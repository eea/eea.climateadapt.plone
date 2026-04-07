# -*- coding: utf-8 -*-
"""A tile to implement the transregional select dropdown"""

from eea.climateadapt.interfaces import ITransnationalRegionMarker
# from collective.cover.tiles.base import IPersistentCoverTile, PersistentCoverTile
from plone.tiles.interfaces import IPersistentTile
from plone.tiles.tile import PersistentTile
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implementer

from eea.climateadapt.translation.utils import TranslationUtilsMixin, translated_url


class ITransRegionalSelectTile(IPersistentTile):
    title = schema.TextLine(
        title=str("Title"),
        required=False,
    )

    region = schema.Choice(
        title=str("Region"),
        vocabulary="eea.climateadapt.regions",
        required=True,
    )


@implementer(ITransRegionalSelectTile)
class TransRegionalSelectTile(PersistentTile, TranslationUtilsMixin):
    """TransRegionalSelect tile

    Shows a dropdown select for a region
    """

    index = ViewPageTemplateFile("pt/transregional_select.pt")

    is_configurable = False
    is_editable = True
    is_droppable = False
    short_name = "Select trans region"

    def is_empty(self):
        return False

    def regions(self):
        return get_regions(self.current_lang)

    def countries(self):
        return get_countries(self.context, self.data, self.current_lang)
