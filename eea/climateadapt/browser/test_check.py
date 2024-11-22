import csv
import logging
from datetime import date

import transaction
from plone import api
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from z3c.relationfield import RelationValue

from zope.component import getUtility
from zope.intid.interfaces import IIntIds

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

class TestExistUrls():
    """ Test if URLs exist
    """

    def get_object(self, path):
        local_path = path.replace('http://','')
        local_path = local_path.replace('https://','')

        local_path = local_path[local_path.find('/'):]
        local_path = local_path[1:]

        #import pdb; pdb.set_trace()
        site = api.portal.get()
        try:
            object = site.restrictedTraverse(local_path)
            if object:
                return object;
        except Exception as e:
            return None

        return None


    def list(self):

        catalog = api.portal.get_tool('portal_catalog')

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
            item['state'] = row[2]
            item['url'] = row[3]

            if len(item['state'])<1:
                continue;

            if len(item['url'])<5:
                continue;

            obj = self.get_object(item['url'])

            urlExist = True

            if not obj:
                logger.warning("Object not found: %s", item['url'])
                urlExist = False
            else:
                logger.info("Objecf found: %s", item['url'])

            #transaction.savepoint()
            response.append({
               'title': item['title'],
                'state': item['url'],
                'url': item['url'],
                'exist': urlExist
            })

        return response
