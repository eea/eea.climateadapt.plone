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
                if brain.getObject().year and isinstance(brain.getObject().year, int) and brain.getObject().year>0:
                    brainUpdated = True
                    brain.getObject().publication_date = date(brain.getObject().year, 1, 1)
                if isinstance(brain.getObject().health_impacts, str):
                    brainUpdated = True
                    temp = []
                    temp.append(brain.getObject().health_impacts)
                    brain.getObject().health_impacts = temp

                if brainUpdated:
                    brain.getObject()._p_changed = True

                res.append({'title':brain.getObject().title,'id':brain.UID,'url':brain.getURL(),'year':brain.getObject().year,
                        'publication_date':brain.getObject().publication_date,
                        'health_impacts':brain.getObject().health_impacts
                    })

        return res
