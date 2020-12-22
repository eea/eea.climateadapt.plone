import csv
import logging
from datetime import date

import transaction
from plone import api
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue

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


class OrganisationLogo():
    """ Migrate organisation logo field
    """

    def list(self):
        response = []

        catalog = api.portal.get_tool('portal_catalog')
        for _type in DB_ITEM_TYPES:
            brains = catalog.searchResults(portal_type=_type)

            for brain in brains:
                obj = brain.getObject()

                logger.info("Organisation: %s", brain.getURL())
                # if hasattr(obj, 'image') \
                #        and obj.image:
                if hasattr(obj, 'logo') \
                        and obj.logo:
                    # if hasattr(obj, 'thumbnail') \
                    #        and obj.thumbnail:
                    # obj.image = obj.logo
                    # obj._p_changed = True

                    response.append({
                        'title': obj.title,
                        'url': brain.getURL()
                    })

                    logger.info("Organisation has logo: %s", brain.getURL())
        logger.info("Articles in response: %s", len(response))
        return response


class SourceToRichText():
    """ Migrate funding_programme field
    """

    def list(self):
        catalog = api.portal.get_tool('portal_catalog')

        DB_ITEM_TYPES = [
            'eea.climateadapt.guidancedocument',
            'eea.climateadapt.indicator',
            'eea.climateadapt.informationportal',
            'eea.climateadapt.organisation',
            'eea.climateadapt.publicationreport',

            'eea.climateadapt.tool'

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
                    logger.info("Migrated source type for obj: %s",
                                brain.getURL())


class OrganisationOrganisational():
    """ Migrate funding_programme field
    """

    def list(self):
        catalog = api.portal.get_tool('portal_catalog')

        DB_ITEM_TYPES = [
            #'eea.climateadapt.guidancedocument',
            #'eea.climateadapt.indicator',
            #'eea.climateadapt.informationportal',
            'eea.climateadapt.organisation',
            #'eea.climateadapt.publicationreport',
            #'eea.climateadapt.tool'
        ]

        i = 0
        for _type in DB_ITEM_TYPES:
            i += 1
            if i % 100 == 0:
                transaction.savepoint()

            brains = catalog.searchResults(portal_type=_type)

            for brain in brains:
                obj = brain.getObject()

                obj.organisational_links = tuple()
                obj._p_changed = True


DRMKC_SRC = 'https://drmkc.jrc.ec.europa.eu/knowledge/PROJECT-EXPLORER/Projects-Explorer#project-explorer/631/'


class DrmkcSource():
    """ Override to hide files and images in the related content viewlet
    """

    def process_type(self, _type):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(portal_type=_type)

        res = []

        for brain in brains:
            obj = brain.getObject()

            if hasattr(obj, 'partners_source_link'):
                link = obj.partners_source_link
                if link is not None and link.startswith(DRMKC_SRC):
                    obj.partners_source_link = link.replace(
                        'project-explorer/631/', 'project-explorer/1035/')
                    obj._p_changed = True

                    logger.info("Update partner link obj: %s",
                                brain.getURL())

                    res.append(
                        {
                            'title': obj.title,
                            'url': brain.getURL(),
                        }
                    )

        return res

    def list(self):
        # issues/125183

        res = []

        i = 0
        for _type in DB_ITEM_TYPES:
            i += 1
            if i % 100 == 0:
                transaction.savepoint()
            res.extend(self.process_type(_type))

        return res
