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

class YearToDate():
    """ Override to hide files and images in the related content viewlet
    """

    def list(self):
        #overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool('portal_catalog')
        types = ['eea.climateadapt.adaptationoption',
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
