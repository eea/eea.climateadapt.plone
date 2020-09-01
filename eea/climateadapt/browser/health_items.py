from plone import api
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import urlparse
from zope.schema import Choice
from z3c.relationfield import RelationValue
from zope.intid.interfaces import IIntIds
from zope.component import getUtility
from eea.climateadapt.vocabulary import _health_impacts

import csv
import StringIO
import sys
import logging

logger = logging.getLogger('eea.climateadapt')

class UpdateFields():
    """ Override to hide files and images in the related content viewlet
    """

    def list(self):
        map_organisations = {
            'european-commission-directorate-general-joint-research-centre-jrc': 1,
            'copernicus-climate-change-service-c3s': 1,
            'who-regional-office-for-europe-who-europe': 1,
            'european-centre-for-disease-prevention-and-control-ecdc': 1,
            'european-environment-agency-eea': 1,
            'european-commission': 1,
            'european-commission-directorate-general-health-and-food-safety-dg-sante': 1,
            'lancet-countdown': 1,
            'european-food-safety-authority-efsa': 1,
            'european-commission-directorate-general-for-climate-action-dg-clima': 1
        }

        util = getUtility(IIntIds, context=self.context)
        for title in map_organisations.keys():
            orgs = self.context.portal_catalog.searchResults(portal_type="eea.climateadapt.organisation", getId=title)
            if not orgs:
                logger.warning("Organisation not found: %s", title)
                return
            #org = orgs[0].getObject()
            map_organisations[title] = util.getId(orgs[0].getObject())

        #import pdb; pdb.set_trace()

        health_impacts = dict(_health_impacts)

        res = []

        itemsFound = []
        portal = api.portal.get()

        fileUploaded = self.request.form.get('fileToUpload', None)

        if not (fileUploaded != None):
            return

        reader = csv.reader(
            fileUploaded,
            delimiter=',',
            quotechar='"',
        #    dialect='excel',
        )

        for row in reader:
            item = {}
            item['title'] = row[0]
            item['include_in_observatory'] = row[3]
            item['health_impact'] = row[7]
            item['partner_organisation'] = row[8]
            item['url'] = row[11]

            if (not itemsFound):        # bypass the header in the CSV file
                itemsFound.append(item)
                continue

            currentPath =  urlparse.urlparse(item['url']).path
            obj = portal.unrestrictedTraverse(currentPath[1:])
            if obj:
                logger.info("Processing Health Obs import: %s", obj.absolute_url())
                if item['include_in_observatory'] == 'Yes':
                    obj.include_in_observatory = True
                else:
                    obj.include_in_observatory = False

                if item['partner_organisation'] in map_organisations:
                    relationId = map_organisations[item['partner_organisation']]
                    logger.info("Set relationship %s", relationId)
                    obj.partner_organisation = RelationValue(relationId)
                    #obj.health_impacts = Choice(healthImpactChoice.value)
                obj.health_impacts = health_impacts.get(item['health_impact'], None)
                obj._p_changed = True

    # orgs_results = catalog.searchResults(**{'portal_type': 'eea.climateadapt.organisation', 'review_state': 'published'})

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(**{'portal_type': 'eea.climateadapt.aceproject', 'review_state': 'published'})
        for brain in brains:
            if brain.UID in itemsFound:
                csvData = itemsFound[brain.UID]
                obj = brain.getObject()
                obj.funding = itemsFound[brain.UID]['funding']
                obj._p_changed = True

            res.append({'title':brain.getObject().title,'id':brain.UID,'url':brain.getURL(),'funding':brain.getObject().funding,
                    'include_in_observatory':brain.getObject().include_in_observatory,
                    'health_impacts':brain.getObject().health_impacts
                    })

        return res
