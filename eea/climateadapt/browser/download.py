import csv
import logging
import urlparse
from datetime import date
from io import BytesIO as StringIO

import transaction
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from eea.climateadapt.vocabulary import _health_impacts
from plone import api
from plone.api import portal
from plone.api.portal import get_tool
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from Products.Five.browser import BrowserView
from z3c.relationfield import RelationValue
from zc.relation.interfaces import ICatalog


logger = logging.getLogger("eea.climateadapt")


class CaseStudiesCSV(BrowserView):
    """ Download CSV file with contacts for case studies """
    def __call__(self):
        out = StringIO()
        csv_writer = csv.writer(out, dialect='excel', delimiter=',')
        #csv_writer.writer(writer_file, dialect=dialect, delimiter=self.delimiter)

        self.request.response.setHeader('Content-type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="case_studies_contact.csv"')

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.casestudy",
                ]
            }
        )

        csv_writer.writerow([
                'Title',
                'Url',
                'Status',
                'Contact',
                'Longitude',
                'Latitude'
                ])
        for brain in brains:
            obj = brain.getObject()
            line = [
                obj.title.encode('utf-8'),
                brain.getURL(),
                brain.review_state,
                obj.contact.raw.encode('utf-8'),
                str(obj.geolocation.longitude if obj.geolocation and hasattr(obj.geolocation, 'longitude') else ''),
                str(obj.geolocation.latitude if obj.geolocation and hasattr(obj.geolocation, 'latitude') else '')
                ]
            csv_writer.writerow(line)

        out.seek(0)
        return out.getvalue()


class KeywordsTagsCSV(BrowserView):
    """ Download CSV file with keywords/special_tags for all objects """
    def __call__(self):
        out = StringIO()
        csv_writer = csv.writer(out, dialect='excel', delimiter=',')
        keywords = []
        tags = []

        self.request.response.setHeader('Content-type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="keywords_tags.csv"')

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults()

        csv_writer.writerow([
                'Keywords',
                'Tags'
                ])
        for brain in brains:
            obj = brain.getObject()

            if hasattr(obj, 'keywords'):
                keys = getattr(obj, 'keywords', [])
                if keys not in [None, []]:
                    for keyword in keys:
                        keywords.append(keyword)

            if hasattr(obj, 'special_tags'):
                sp_tags = getattr(obj, 'special_tags', [])
                if sp_tags not in [None, []]:
                    for tag in sp_tags:
                        tags.append(tag)

        # convert to set and then list to get rid of duplicates
        keywords_set = set(keywords)
        tags_set = set(tags)

        keywords = list(keywords_set)
        tags = list(tags_set)

        line = [
            keywords,
            tags,
            ]
        csv_writer.writerow(line)

        out.seek(0)
        return out.getvalue()
