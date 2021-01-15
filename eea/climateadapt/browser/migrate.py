import csv
import logging
import urlparse
from datetime import date

import transaction
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from eea.climateadapt.vocabulary import _health_impacts
from plone import api
from plone.api import portal
from plone.api.portal import get_tool
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from Products.Five.browser import BrowserView
from z3c.relationfield import RelationValue

# from zope.schema import Choice
# from zope.schema.interfaces import IVocabularyFactory
# import StringIO
# import sys


logger = logging.getLogger("eea.climateadapt")


DB_ITEM_TYPES = [
    "eea.climateadapt.adaptationoption",
    "eea.climateadapt.aceproject",
    "eea.climateadapt.casestudy",
    "eea.climateadapt.guidancedocument",
    "eea.climateadapt.indicator",
    "eea.climateadapt.informationportal",
    "eea.climateadapt.organisation",
    "eea.climateadapt.publicationreport",
    "eea.climateadapt.tool",
    "eea.climateadapt.video",
]


class ConvertSiteOrigin(BrowserView):
    """Convert the site origin from string to list"""

    def __call__(self):
        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.aceproject",
                    "eea.climateadapt.casestudy",
                    "eea.climateadapt.adaptationoption",
                    "eea.climateadapt.guidancedocument",
                    "eea.climateadapt.indicator",
                    "eea.climateadapt.informationportal",
                    "eea.climateadapt.organisation",
                    "eea.climateadapt.publicationreport",
                    "eea.climateadapt.researchproject",
                    "eea.climateadapt.tool",
                    "eea.climateadapt.video",
                ]
            }
        )

        for brain in brains:
            obj = brain.getObject()
            origin_website = obj.origin_website
            source = obj.source

            if obj.source == "DRMKC" and not obj.origin_website:
                obj.origin_website = [source]
                logger.info("Migrated site origin : %s %s", brain.getURL(), obj.origin_website)

            elif origin_website and isinstance(origin_website, str):
                obj.origin_website = [origin_website]
                logger.info("Migrated site origin : %s %s", brain.getURL(), obj.origin_website)

            elif origin_website is None:
                obj.origin_website = []
                logger.info("Migrated site origin : %s %s", brain.getURL(), obj.origin_website)

            else:
                continue

            obj._p_changed = True
            obj.reindexObject()

        return "done"


class YearToDate:
    """Override to hide files and images in the related content viewlet"""

    def list(self):
        # overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool("portal_catalog")
        res = []

        i = 0
        for _type in DB_ITEM_TYPES:
            i += 1
            if i % 100 == 0:
                transaction.savepoint()

            brains = catalog.searchResults(portal_type=_type)

            for brain in brains:
                obj = brain.getObject()

                if hasattr(obj, "year"):
                    if obj.year and isinstance(obj.year, int) and obj.year > 0:
                        obj.publication_date = date(obj.year, 1, 1)
                        obj._p_changed = True

                    logger.info("Migrated year for obj: %s", brain.getURL())

                    res.append(
                        {
                            "title": obj.title,
                            "id": brain.UID,
                            "url": brain.getURL(),
                            "year": obj.year if hasattr(obj, "year") else "",
                        }
                    )

        return res


class HealthImpacts:
    """Migrate the health_impacts attribute from a simple string to a list"""

    def list(self):
        # overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool("portal_catalog")

        res = []
        for _type in DB_ITEM_TYPES:
            brains = catalog.searchResults(
                portal_type=_type, include_in_observatory=True
            )
            for brain in brains:
                obj = brain.getObject()

                if hasattr(obj, "health_impacts") and isinstance(
                    obj.health_impacts, str
                ):
                    obj.health_impacts = [obj.health_impacts]
                    obj._p_changed = True
                    logger.info("Migrated health impact for obj: %s %s", brain.getURL(), obj.health_impacts)

                    res.append(
                        {
                            "title": obj.title,
                            "id": brain.UID,
                            "url": brain.getURL(),
                            # 'publication_date': obj.publication_date,
                            "health_impacts": obj.health_impacts,
                        }
                    )

        return res


class FundingProgramme:
    """Migrate funding_programme field"""

    def list(self):
        response = []
        fileUploaded = self.request.form.get("fileToUpload", None)

        if not fileUploaded:
            return response

        reader = csv.reader(
            fileUploaded,
            delimiter=",",
            quotechar='"',
            #    dialect='excel',
        )

        # need condition for "Yes"
        for row in reader:
            item = {}
            item["title"] = row[0]
            item["funding_programme"] = row[3]
            item["url"] = row[4]
            item["uid"] = row[6]

            obj = api.content.get(UID=item["uid"])

            if not obj:
                continue

            obj.funding_programme = item["funding_programme"]
            obj._p_changed = True
            response.append(
                {
                    "title": obj.title,
                    "url": item["url"],
                    "funding_programme": obj.funding_programme,
                }
            )
            logger.info("Migrated funding programme for obj: %s", obj.absolute_url())

        return response


# 126085
class ContributingOrganisationPartner():
    """ Migrate funding_programme field
    """

    def get_object(self, path):
        local_path = path.replace('http://', '')
        local_path = local_path.replace('https://', '')

        local_path = local_path[local_path.find('/'):]
        local_path = local_path[1:]

        #import pdb; pdb.set_trace()
        site = api.portal.get()
        try:
            object = site.restrictedTraverse(local_path)
            if object:
                return object
        except Exception, e:
            return None

        return None

    def list(self):

        catalog = api.portal.get_tool('portal_catalog')

        map_organisations = {
            'World Health Organization - Regional Office for Europe - Climate-ADAPT (europa.eu)':
                {'url': 'who-regional-office-for-europe-who-europe', 'id': 0, 'object': None},
            'World Health Organization - Climate-ADAPT (europa.eu)':
                {'url': 'world-health-organization', 'id': 0, 'object': None}
        }

        util = getUtility(IIntIds, context=self.context)
        for title in map_organisations.keys():
            orgs = self.context.portal_catalog.searchResults(
                portal_type="eea.climateadapt.organisation", getId=map_organisations[title]['url'])
            if not orgs:
                logger.warning("Organisation not found: %s", title)
            else:
                map_organisations[title]['id'] = util.getId(orgs[0].getObject())
                map_organisations[title]['object'] = orgs[0].getObject()

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

        for row in reader:
            item = {}
            item['title'] = row[0]
            item['url'] = row[10]
            item['partners'] = row[17]

            if len(item['url']) < 5:
                continue

            obj = self.get_object(item['url'])

            if not obj:
                logger.warning("Object not found: %s", item['url'])
                continue

            if item['partners'] not in map_organisations:
                logger.warning("Partner not found: %s [%s]", item['url'], item['partners'])
                continue

            partner_object_id = map_organisations[item['partners']]['id']
            if not partner_object_id:
                logger.warning("Partner not match: %s [%s]", item['url'], item['partners'])
                continue

            if type(obj.contributors) is not list:
                obj.contributors = []

            for contibutor_data in obj.contributors:
                if partner_object_id == util.getId(contibutor_data.to_object):
                    partner_object_id = None
                    break

            if not partner_object_id:
                logger.info("Partner already set: %s [%s]", item['url'], item['partners'])
            else:
                logger.info("Partner set: %s [%s]", item['url'], item['partners'])
                obj.contributors.append(RelationValue(partner_object_id))
                obj._p_changed = True

            # transaction.savepoint()
            response.append({
                'title': obj.title,
                'url': item['url'],
            })

        return response


class OrganisationLogo:
    """Migrate organisation logo field"""

    def list(self):
        response = []

        catalog = api.portal.get_tool("portal_catalog")
        for _type in DB_ITEM_TYPES:
            brains = catalog.searchResults(portal_type=_type)

            for brain in brains:
                obj = brain.getObject()

                # if hasattr(obj, 'image') \
                #        and obj.image:
                if hasattr(obj, "logo") and obj.logo:
                    # if hasattr(obj, 'thumbnail') \
                    #        and obj.thumbnail:
                    obj.image = obj.logo
                    obj._p_changed = True

                    response.append({"title": obj.title, "url": brain.getURL()})
                    logger.info("Organisation logo: %s", brain.getURL())

        logger.info("Articles with logo in response: %s", len(response))
        return response


class SourceToRichText:
    """Migrate funding_programme field"""

    def list(self):
        catalog = api.portal.get_tool("portal_catalog")

        DB_ITEM_TYPES = [
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.tool",
        ]

        i = 0
        for _type in DB_ITEM_TYPES:
            i += 1
            if i % 100 == 0:
                transaction.savepoint()

            brains = catalog.searchResults(portal_type=_type)

            for brain in brains:
                obj = brain.getObject()

                if (
                    hasattr(obj, "source")
                    and not isinstance(obj.source, RichText)
                    and not isinstance(obj.source, RichTextValue)
                ):
                    obj.source = RichTextValue(obj.source)
                    obj._p_changed = True
                    logger.info("Migrated source type for obj: %s", brain.getURL())


class OrganisationOrganisational:
    """Migrate funding_programme field"""

    def list(self):
        catalog = api.portal.get_tool("portal_catalog")

        DB_ITEM_TYPES = [
            # 'eea.climateadapt.guidancedocument',
            # 'eea.climateadapt.indicator',
            # 'eea.climateadapt.informationportal',
            "eea.climateadapt.organisation",
            # 'eea.climateadapt.publicationreport',
            # 'eea.climateadapt.tool'
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


DRMKC_SRC = "https://drmkc.jrc.ec.europa.eu/knowledge/PROJECT-EXPLORER/Projects-Explorer#project-explorer/631/"


class DrmkcSource:
    """Override to hide files and images in the related content viewlet"""

    def process_type(self, _type):
        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog.searchResults(portal_type=_type)

        res = []

        for brain in brains:
            obj = brain.getObject()

            if hasattr(obj, "partners_source_link"):
                link = obj.partners_source_link

                if link is not None and link.startswith(DRMKC_SRC):
                    obj.partners_source_link = link.replace(
                        "project-explorer/631/", "project-explorer/1035/"
                    )
                    obj._p_changed = True

                    logger.info("Update partner link obj: %s", brain.getURL())

                    res.append(
                        {
                            "title": obj.title,
                            "url": brain.getURL(),
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


logger = logging.getLogger("eea.climateadapt")


class UpdateHealthItemsFields:
    """Override to hide files and images in the related content viewlet"""

    def list(self):
        map_organisations = {
            "european-commission-directorate-general-joint-research-centre-jrc": 1,
            "copernicus-climate-change-service-c3s": 1,
            "who-regional-office-for-europe-who-europe": 1,
            "european-centre-for-disease-prevention-and-control-ecdc": 1,
            "european-environment-agency-eea": 1,
            "european-commission": 1,
            "european-commission-directorate-general-health-and-food-safety-dg-sante": 1,
            "lancet-countdown": 1,
            "european-food-safety-authority-efsa": 1,
            "european-commission-directorate-general-for-climate-action-dg-clima": 1,
        }

        util = getUtility(IIntIds, context=self.context)
        for title in map_organisations.keys():
            orgs = self.context.portal_catalog.searchResults(
                portal_type="eea.climateadapt.organisation", getId=title
            )
            if not orgs:
                logger.warning("Organisation not found: %s", title)
                return
            # org = orgs[0].getObject()
            map_organisations[title] = util.getId(orgs[0].getObject())

        health_impacts = dict(_health_impacts)

        res = []

        itemsFound = []
        portal = api.portal.get()

        fileUploaded = self.request.form.get("fileToUpload", None)

        if not (fileUploaded is not None):
            return

        reader = csv.reader(
            fileUploaded,
            delimiter=",",
            quotechar='"',
            #    dialect='excel',
        )

        for row in reader:
            item = {}
            item["title"] = row[0]
            item["include_in_observatory"] = row[3]
            item["health_impact"] = row[7]
            item["partner_organisation"] = row[8]
            item["url"] = row[11]

            if not itemsFound:  # bypass the header in the CSV file
                itemsFound.append(item)
                continue

            currentPath = urlparse.urlparse(item["url"]).path
            try:
                obj = portal.unrestrictedTraverse(currentPath[1:])
            except Exception, e:
                logger.warning("NOT FOUND: %s", item['url'])
                continue

            if obj:
                logger.info("Object process: %s", item['url'])
                if item["include_in_observatory"] == "Yes":
                    obj.include_in_observatory = True
                else:
                    obj.include_in_observatory = False

                if item["partner_organisation"] in map_organisations:
                    relationId = map_organisations[item["partner_organisation"]]
                    obj.partner_organisation = RelationValue(relationId)
                    # obj.health_impacts = Choice(healthImpactChoice.value)

                obj.health_impacts = [health_impacts.get(item["health_impact"], None)]
                obj._p_changed = True

        # orgs_results = catalog.searchResults(**{'portal_type': 'eea.climateadapt.organisation', 'review_state': 'published'})

        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog.searchResults(
            **{
                "portal_type": "eea.climateadapt.aceproject",
                "review_state": "published",
            }
        )
        for brain in brains:
            if brain.UID in itemsFound:
                # csvData = itemsFound[brain.UID]
                obj = brain.getObject()
                obj.funding = itemsFound[brain.UID]["funding"]
                obj._p_changed = True

            res.append(
                {
                    "title": brain.getObject().title,
                    "id": brain.UID,
                    "url": brain.getURL(),
                    "funding": brain.getObject().funding,
                    "include_in_observatory": brain.getObject().include_in_observatory,
                    "health_impacts": brain.getObject().health_impacts,
                }
            )

        return res
