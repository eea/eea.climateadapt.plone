import csv
import logging
import urlparse
from datetime import date

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

# from zope.schema import Choice
# from zope.schema.interfaces import IVocabularyFactory
# import StringIO
# import sys


logger = logging.getLogger("eea.climateadapt")


class CaseStudiesCSV(BrowserView):
    """Download CSV file with contacts for case studies"""
    def __call__(self):
        from io import BytesIO as StringIO
        import csv
        out = StringIO()
        csv_writer = csv.writer(out, dialect='excel', delimiter=',')
        #csv_writer.writer(writer_file, dialect=dialect, delimiter=self.delimiter)

        self.request.response.setHeader('Content-type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="case_studies_contact.csv"')

        #print('A,B')
        #print('0,1')
        #print('10,11')
        #csv_writer.writerow(['a'])
        #csv_writer.writerow(['0'])
        #csv_writer.writerow(['10'])


        #return "a,b,c\r\n0,1,2\r\n10,11,12\r\n"

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.casestudy",
                ]
            }
        )

        print('Title,Url,Status,Contact,Longitude,Latitude');
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
