""" Cards listing
"""

import json
import urllib

from collective.cover.tiles.base import (IPersistentCoverTile,
                                         PersistentCoverTile)
from eea.climateadapt.translation.utils import get_current_language
from zope import schema
from zope.interface import implements

from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ICardsTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=u"Title",
        required=True,
    )

    uuid = schema.TextLine(
        title=u"UUID",
        required=False,
        readonly=True,
    )

    # view_name = schema.Choice(
    #     title=_(u"Custom tile view renderer"),
    #     values=["card_indicator", "card_organisation"],
    #     required=False,
    # )


class CardsTile(PersistentCoverTile):
    """Generic view tile"""

    implements(ICardsTile)

    index = ViewPageTemplateFile("pt/cards.pt")

    is_configurable = True
    is_editable = True
    is_droppable = True
    short_name = u"Cards"

    def is_empty(self):
        return (
            self.data.get("uuid", None) is None
            or uuidToObject(self.data.get("uuid")) is None
        )

    def get_context(self):
        uuid = self.data.get("uuid")
        if uuid:
            return uuidToObject(uuid)

    def cards(self):
        context = self.get_context()
        if not context:
            return []

        #import pdb; pdb.set_trace()
        #return context.results()

        # Will return items only for current language instead
        language = get_current_language(self.context, self.request)
        results = context.results()
        response = []
        for result in results:
            if result.getPath().startswith("/cca/"+language):
                response.append(result)
        return response

    def accepted_ct(self):
        return ["Collection"]

    def populate_with_object(self, obj):
        #import pdb; pdb.set_trace()
        super(CardsTile, self).populate_with_object(obj)  # check permission

        if obj.portal_type in self.accepted_ct():

            data_mgr = ITileDataManager(self)
            data_mgr.set({"uuid": IUUID(obj)})

    def render_tile(self, info):
        pass


class IndicatorCard(BrowserView):
    """Indicator @@card view"""

    def indicator_link(self):
        language = get_current_language(self.context, self.request)
        link = "/"+language+"/observatory/++aq++" + "/".join(self.context.getPhysicalPath()[2:])
        #link = link.replace("++aq++en/", "++aq++"+language+"/")
        link = link.replace("++aq++"+language+"/", "++aq++")
        return link


class OrganisationCard(BrowserView):
    """Organisation @@card view"""

    # index = ViewPageTemplateFile("pt/card_organisation.pt")
    def contact_link(self):
        contact = getattr(self.context, "contact", "") or ""
        if contact.startswith("mailto"):
            return contact

        if contact.startswith("http"):
            return contact

        if "@" in contact:
            return "mailto:%s" % contact

        return "https://%s" % contact

    def contributions_link(self):
        org = ''

        map_contributor_values = {
            "copernicus-climate-change-service-ecmw": "Copernicus Climate Change Service and Copernicus Atmosphere Monitoring Service",
            "european-centre-for-disease-prevention-and-control-ecdc": "European Centre for Disease Prevention and Control",
            "european-commission": "European Commission",
            "european-environment-agency-eea": "European Environment Agency",
            "european-food-safety-authority": "European Food Safety Authority",
            "lancet-countdown": "Lancet Countdown",
            "who-regional-office-for-europe-who-europe": "WHO Regional Office for Europe",
            "world-health-organization": "World Health Organization"
        }

        if self.context.id in map_contributor_values:
            org = map_contributor_values[self.context.id]

        t = {
            u"function_score": {
                u"query": {
                    u"bool": {
                        u"filter": {
                            u"bool": {
                                u"should": [
                                    {u"term": {u"partner_contributors": org}}
                                ]
                            }
                        },
                    }
                }
            }
        }

        q = {"query": t}

        return "/observatory/catalogue/?source=" + urllib.quote(json.dumps(q))

    def website_link(self):
        websites = getattr(self.context, "websites", [])
        if not websites:
            return None
        return websites[0]

    def organisation_link(self):
        language = get_current_language(self.context, self.request)
        link = "/"+language+"/observatory/++aq++" + "/".join(self.context.getPhysicalPath()[2:])
        link = link.replace("++aq++"+language+"/", "++aq++")
        return link
