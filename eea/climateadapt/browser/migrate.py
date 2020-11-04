import csv
import logging
from datetime import date
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue

import transaction

from plone import api

# import StringIO
# import sys
# import urlparse
# from eea.climateadapt.vocabulary import _health_impacts
# from zope.component import getUtility
# from zope.intid.interfaces import IIntIds
# from zope.schema import Choice
# from zope.schema.interfaces import IVocabularyFactory

# from z3c.relationfield import RelationValue

logger = logging.getLogger('eea.climateadapt')


DB_ITEM_TYPES = [
    'eea.climateadapt.adaptationoption',
    'eea.climateadapt.aceproject',
    'eea.climateadapt.casestudy',
    'eea.climateadapt.guidancedocument',
    'eea.climateadapt.indicator',
    'eea.climateadapt.informationportal',
    'eea.climateadapt.organisation',
    'eea.climateadapt.publicationreport',

    'eea.climateadapt.tool',
    'eea.climateadapt.video'
]


class YearToDate():
    """ Override to hide files and images in the related content viewlet
    """

    def list(self):
        # overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool('portal_catalog')
        res = []

        i = 0
        for _type in DB_ITEM_TYPES:
            i += 1
            if i % 100 == 0:
                transaction.savepoint()

            brains = catalog.searchResults(portal_type=_type)

            for brain in brains:
                obj = brain.getObject()

                if hasattr(obj, 'year'):
                    if obj.year and isinstance(obj.year, int) and obj.year > 0:
                        obj.publication_date = date(obj.year, 1, 1)
                        obj._p_changed = True

                    logger.info("Migrated year for obj: %s", brain.getURL())

                    res.append(
                        {
                            'title': obj.title,
                            'id': brain.UID,
                            'url': brain.getURL(),
                            'year': obj.year if hasattr(obj, 'year') else '',
                        }
                    )

        return res


class HealthImpacts():
    """ Migrate the health_impacts attribute from a simple string to a list
    """

    def list(self):
        # overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool('portal_catalog')

        res = []
        for _type in DB_ITEM_TYPES:
            brains = catalog.searchResults(
                portal_type=_type, include_in_observatory=True
            )
            for brain in brains:
                obj = brain.getObject()

                if hasattr(obj, 'health_impacts') and \
                        isinstance(obj.health_impacts, str):
                    obj.health_impacts = [obj.health_impacts]
                    obj._p_changed = True
                    logger.info("Migrated health impact for obj: %s",
                                brain.getURL())

                    res.append(
                        {
                            'title': obj.title,
                            'id': brain.UID,
                            'url': brain.getURL(),
                            # 'publication_date': obj.publication_date,
                            'health_impacts': obj.health_impacts
                        }
                    )

        return res


class FundingProgramme():
    """ Migrate funding_programme field
    """

    def list(self):
        response = []
        fileUploaded = self.request.form.get('fileToUpload', None)

        if not fileUploaded:
            return response

        reader = csv.reader(
            fileUploaded,
            delimiter=',',
            quotechar='"',
            #    dialect='excel',
        )

        # need condition for "Yes"
        for row in reader:
            item = {}
            item['title'] = row[0]
            item['funding_programme'] = row[3]
            item['url'] = row[4]
            item['uid'] = row[6]

            obj = api.content.get(UID=item['uid'])

            if not obj:
                continue

            obj.funding_programme = item['funding_programme']
            obj._p_changed = True
            response.append({
                'title': obj.title,
                'url': item['url'],
                'funding_programme': obj.funding_programme
            })
            logger.info("Migrated funding programme for obj: %s",
                        obj.absolute_url())

        return response


class SourceToRichText():
    """ Migrate funding_programme field
    """

    def list(self):
        catalog = api.portal.get_tool('portal_catalog')
        res = []

        DB_ITEM_TYPES = [
            'eea.climateadapt.organisation'
        ]

        i = 0
        for _type in DB_ITEM_TYPES:
            i += 1
            if i % 100 == 0:
                transaction.savepoint()

            brains = catalog.searchResults(portal_type=_type)

            for brain in brains:
                obj = brain.getObject()

                if hasattr(obj, 'source') \
                        and not isinstance(obj.source, RichText) \
                        and not isinstance(obj.source, RichTextValue):
                    obj.source = RichTextValue(obj.source)
                    obj._p_changed = True
                    logger.info("Migrated source type for obj: %s", brain.getURL())
