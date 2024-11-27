import csv
import logging
# import urllib.parse
# from datetime import date
from io import BytesIO as StringIO

from plone.api.portal import get_tool
from Products.Five.browser import BrowserView

# import urlparse
# from datetime import date

# import transaction
# from zope.component import getUtility
# from zope.intid.interfaces import IIntIds
#
# from zope.lifecycleevent import ObjectModifiedEvent
# from zope.event import notify
# from eea.climateadapt.vocabulary import _health_impacts
# from plone import api
# from plone.api import portal

# from plone.app.textfield import RichText
# from plone.app.textfield.value import RichTextValue

# from z3c.relationfield import RelationValue
# from zc.relation.interfaces import ICatalog


logger = logging.getLogger("eea.climateadapt")


class CaseStudiesCSV(BrowserView):
    """Download CSV file with contacts for case studies"""

    def __call__(self):
        out = StringIO()
        csv_writer = csv.writer(out, dialect="excel", delimiter=",")
        # csv_writer.writer(writer_file, dialect=dialect, delimiter=self.delimiter)

        self.request.response.setHeader("Content-type", "text/csv")
        self.request.response.setHeader(
            "Content-Disposition", 'attachment; filename="case_studies_contact.csv"'
        )

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.casestudy",
                ]
            }
        )

        csv_writer.writerow(
            ["Title", "Url", "Status", "Contact", "Longitude", "Latitude"]
        )
        for brain in brains:
            obj = brain.getObject()
            line = [
                obj.title.encode("utf-8"),
                brain.getURL(),
                brain.review_state,
                obj.contact.raw.encode("utf-8"),
                str(
                    obj.geolocation.longitude
                    if obj.geolocation and hasattr(obj.geolocation, "longitude")
                    else ""
                ),
                str(
                    obj.geolocation.latitude
                    if obj.geolocation and hasattr(obj.geolocation, "latitude")
                    else ""
                ),
            ]
            csv_writer.writerow(line)

        out.seek(0)
        return out.getvalue()


class KeywordsTagsCSV(BrowserView):
    """Download CSV file with keywords/special_tags for all objects"""

    def __call__(self):
        obj_attr = self.request.form.get("attr")
        if not obj_attr:
            return "Missing attr"

        csv_headers = {"keywords": "Keywords", "special_tags": "Tags"}

        out = StringIO()
        csv_writer = csv.writer(out, dialect="excel", delimiter=",")

        entries = []

        self.request.response.setHeader("Content-type", "text/csv")
        self.request.response.setHeader(
            "Content-Disposition", 'attachment; filename="%s.csv"' % obj_attr
        )

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults()

        csv_writer.writerow([csv_headers.get(obj_attr) or obj_attr])

        for brain in brains:
            obj = brain.getObject()

            if hasattr(obj, obj_attr):
                keys = getattr(obj, obj_attr, [])
                if keys not in [None, []]:
                    for key in keys:
                        entries.append(key)

        # convert to set and then list to get rid of duplicates
        entries_set = set(entries)
        entries = list(entries_set)

        for entry in entries:
            line = [
                entry.encode("utf-8"),
            ]
            csv_writer.writerow(line)

        out.seek(0)
        return out.getvalue()
