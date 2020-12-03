from plone import api
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import urlparse
from zope.schema import Choice
from z3c.relationfield import RelationValue
from zope.intid.interfaces import IIntIds
from zope.component import getUtility
from eea.climateadapt.vocabulary import _health_impacts
from datetime import date

import csv
import StringIO
import sys
import logging

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
        #overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool('portal_catalog')
        types = ['eea.climateadapt.adaptationoption',
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
        res = []
        for type in types:
            brains = catalog.searchResults(**{'portal_type': type})
            for brain in brains:
                brainUpdated = False
                obj = brain.getObject()
                if obj.year and isinstance(obj.year, int) and obj.year>0:
                    brainUpdated = True
                    obj.publication_date = date(obj.year, 1, 1)
                if isinstance(obj.health_impacts, str):
                    brainUpdated = True
                    temp = []
                    temp.append(obj.health_impacts)
                    obj.health_impacts = temp

                if brainUpdated:
                    obj._p_changed = True

                res.append({'title':obj.title, 'id':brain.UID,'url':obj,
                        'year':obj.year,
                        'publication_date': obj.publication_date,
                        'health_impacts': obj.health_impacts
                    })

        return res

class HealthImpacts():
    def list(self):
        #overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool('portal_catalog')

        catalog = api.portal.get_tool('portal_catalog')
        types = ['eea.climateadapt.adaptationoption',
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
        res = []
        for type in types:
            #import pdb; pdb.set_trace()
            brains = catalog.searchResults(**{'portal_type': type, 'include_in_observatoty': True})
            for brain in brains:
                brainUpdated = False
                obj = brain.getObject()
                if isinstance(obj.health_impacts, str):
                    brainUpdated = True
                    temp = []
                    temp.append(obj.health_impacts)
                    obj.health_impacts = temp

                if brainUpdated:
                    obj._p_changed = True

                res.append({'title':obj.title, 'id':brain.UID,'url':obj,
                        'publication_date': obj.publication_date,
                        'health_impacts': obj.health_impacts
                    })

        return res

class FundingProgramme():
    def list(self):
        response = []
        fileUploaded = self.request.form.get('fileToUpload', None)

        #import pdb; pdb.set_trace()

        if not (fileUploaded != None):
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
            item['funding_programme'] = row[3]
            item['url'] = row[4]
            item['uid'] = row[6]

            obj = api.content.get(UID=item['uid'])
            if obj:
                obj.funding_programme = item['funding_programme']
                obj._p_changed = True
                response.append({
                    'title': obj.title,
                    'url': item['url'],
                    'funding_programme': obj.funding_programme
                })
            else:
                response.append({
                    'title': item['title'],
                    'url': item['url'],
                    'funding_programme': 'XXXX'
                })

        return response

class ReferenceOtherContributor():
    def list(self):
        #overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool('portal_catalog')
        types = ['eea.climateadapt.adaptationoption',
                #'eea.climateadapt.casestudy',
                #'eea.climateadapt.guidancedocument',
                #'eea.climateadapt.indicator',
                #'eea.climateadapt.informationportal',
                #'eea.climateadapt.publicationreport',

                #'eea.climateadapt.tool',
                'eea.climateadapt.video'
                ]
        res = []
        #return res
        for type in types:
            #import pdb; pdb.set_trace()
            brains = catalog.searchResults(**{'portal_type': type, 'include_in_observatoty': True})
            for brain in brains:
                brainUpdated = False
                obj = brain.getObject()
                if hasattr(obj, 'source'):
                    #import pdb; pdb.set_trace()
                    #if isinstance(obj.source, RichTextValue):
                    #    import pdb; pdb.set_trace()
                    try:
                        obj.other_contributor = obj.source
                    except:
                        obj.other_contributor = obj.source.raw
                    #obj.source = None
                    obj._p_changed = True
                    #import pdb; pdb.set_trace()
                    res.append({'title':obj.title, 'id':brain.UID,'url':obj,
                            'other_contributor': obj.other_contributor
                        })

        return res


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
