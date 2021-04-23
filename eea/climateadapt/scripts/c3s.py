""" A command line ArcGIS client

Call it from a script such as:

    #!/bin/bash
    export LD_LIBRARY_PATH=../../../../../parts/gdal-compile/lib
    export GISPASS=mypass
    ../../../../../bin/zopepy sync_to_arcgis.py "$@"

This commands accepts various parameter. Look at __main__ to see what it does.

# TODO: this script is hackish. Maybe optparse would improve feeling.
"""

import argparse
import json
import logging
import os
import sys
import urllib2
import Zope2
import transaction

from plone.app.textfield.value import RichTextValue

from lxml.etree import Element, SubElement, fromstring, tostring
from eea.climateadapt.scripts import get_plone_site

logger = logging.getLogger('eea.climateadapt')
logging.basicConfig()

SOURCE_URL = 'https://raw.githubusercontent.com/maris-development/c3s-434-portal/static-generator/data/data_consolidated.json'
HOST = 'climate-adapt.eea.europa.eu'
PLONE = "/cca"

def get_source_data():
    response = urllib2.urlopen(SOURCE_URL)
    source_content = response.read()
    return json.loads(source_content)

def save_indicator2(indicator):
        from plone import api
        portal = api.portal.get()

def save_object(obj, indicator):
    print(obj.title)
    print('  ->'+obj.c3s_identifier)
    #if 'C3S_434_021' == obj.c3s_identifier:
    #    import pdb; pdb.set_trace()
    obj.title = indicator['page_title']
    obj.long_description = RichTextValue(indicator['description_detail'])

    obj.definition_app = RichTextValue('<h4>'+indicator['indicator_title']+'</h4>'+indicator['description'])

    obj.overview_app_toolbox_url = indicator['overview']
    obj.overview_app_parameters = '{}'
    if 'indicator' in indicator['vars']['overview'] and indicator['vars']['overview']['indicator']:
        obj.overview_app_parameters = '{workflowParams:{"indicator": "' + indicator['vars']['overview']['indicator'] + '"}}'

    obj.details_app_toolbox_url = indicator['detail']
    obj.details_app_parameters = '{}'
    if 'indicator' in indicator['vars']['detail'] and indicator['vars']['detail']['indicator']:
        obj.details_app_parameters = '{workflowParams:{"indicator": "' + indicator['vars']['detail']['indicator'] + '"}}'

    obj.sectors = []
    obj.climate_impacts = []
    obj._p_changed = True


def save_indicator(indicator):

    print('=============================================')
    #print(type(indicator))
    #print(indicator.keys())
    #print(indicator)

    site = get_plone_site()
    print(indicator['theme'])

    portal_catalog = site.portal_catalog
    brains = portal_catalog.unrestrictedSearchResults(**{'portal_type': 'eea.climateadapt.c3sindicator', 'c3s_identifier': indicator['identifier']})
    indicatorFound = False
    for brain in brains:
        obj = brain.getObject()
        #print(brain.getURL())
        #print('--->'+obj.title)
        try:
            if indicator['identifier'] == obj.c3s_identifier:
                indicatorFound = True
                save_object(obj, indicator)
                transaction.commit()
                print('  UPDATE OBJECT')
        except:
            """"""
            #print("C3S Identifier NOT SET")

    if not indicatorFound:
        folder_path = 'knowledge/european-climate-data-explorer/'
        folder_indicator_id = indicator['theme'].lower().replace(' ','-')

        from plone.dexterity.utils import createContentInContainer

        folder = site.restrictedTraverse(folder_path)
        if folder_indicator_id not in folder.contentIds():
            folder_indicator = createContentInContainer(folder, "Folder", title=indicator['theme'])
        else:
            folder_indicator = folder[folder_indicator_id]


        obj = createContentInContainer(folder_indicator, "eea.climateadapt.c3sindicator", title=indicator['page_title'])
        obj.c3s_identifier = indicator['identifier']
        save_object(obj, indicator)
        transaction.commit()
        print('  INSERT OBJECT')


def main():
    data = get_source_data()
    for indicator_identifier in data['indicators']:
        #print(data['indicators'][indicator_identifier])
        save_indicator(data['indicators'][indicator_identifier])

    print("Total items:" + str(len(data['indicators'])))

if __name__ == "__main__":
    main()
