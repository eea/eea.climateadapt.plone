from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import json
import logging
import urllib2
from plone.api.portal import get_tool
from datetime import datetime

logger = logging.getLogger("eea.climateadapt")


DISCODATA_URL = 'https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_JSON%5D&p=1&nrOfHits=100'

class Page(BrowserView):

    def __call__(self):
        """"""
        data = self.get_data()
        #import pdb; pdb.set_trace()

    def get_data(self):
        #import pdb; pdb.set_trace()
        if 'discodata' not in self.context.__annotations__:
            self.reload_data()
        if (datetime.now() - self.context.__annotations__['discodata']['timestamp']).total_seconds()>60*2:
            self.reload_data()
        return self.context.__annotations__['discodata']['data']

    def reload_data(self):
        response = urllib2.urlopen(DISCODATA_URL)
        self.context.__annotations__['discodata'] = {
                'timestamp': datetime.now(),
                'data': json.loads(response.read())
            }
        logger.info("RELOAD URL %s", DISCODATA_URL)
