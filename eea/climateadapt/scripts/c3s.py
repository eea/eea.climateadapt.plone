""" A command line ArcGIS client

Call it from a script such as:

    #!/bin/bash
    export LD_LIBRARY_PATH=../../../../../parts/gdal-compile/lib
    export GISPASS=mypass
    ../../../../../bin/zopepy sync_to_arcgis.py "$@"

This commands accepts various parameter. Look at __main__ to see what it does.

# TODO: this script is hackish. Maybe optparse would improve feeling.
"""

import datetime
import json
import logging

import transaction
import urllib.request, urllib.error, urllib.parse
from eea.climateadapt.scripts import get_plone_site
from plone.dexterity.utils import createContentInContainer
from plone import api
from plone.app.textfield.value import RichTextValue
from zope.annotation.interfaces import IAnnotations
from collections import OrderedDict

logger = logging.getLogger("eea.climateadapt")
logging.basicConfig()

SOURCE_URL = (
    "https://raw.githubusercontent.com/bopen/c3s-430a-portal/"
    "static-generator-acceptance/data/data_consolidated.json"
)


def get_source_data():
    response = urllib.request.urlopen(SOURCE_URL)
    source_content = response.read()
    return json.loads(source_content, object_pairs_hook=OrderedDict)


def update_object(obj, indicator):
    print((obj.title))
    print(("  ->" + obj.c3s_identifier))

    obj.title = indicator["page_title"]
    obj.indicator_title = indicator["indicator_title"]

    obj.long_description = RichTextValue(indicator["description_general"])
    obj.description = ''
    obj.definition_app = RichTextValue(indicator["description_vis_nav"])

    if isinstance(indicator["theme"], list):
        obj.c3s_theme = indicator["theme"]
    else:
        obj.c3s_theme = [indicator["theme"]]

    obj.overview_app_toolbox_url = indicator["detail"]
    # obj.overview_app_parameters = "{}"
    # if indicator["vars"]["overview"]:
    #    obj.overview_app_parameters = json.dumps(
    #        {"workflowParams": indicator["vars"]["overview"]}
    #    )
    obj.overview_app_parameters = indicator["overview"]

    # obj.details_app_toolbox_url = indicator["detail"]
    # obj.details_app_parameters = "{}"
    # if indicator["vars"]["detail"]:
    #    obj.details_app_parameters = json.dumps(
    #        {"workflowParams": indicator["vars"]["detail"]}
    #    )

    obj.c3s_identifier = indicator.get("identifier", "")
    obj.sectors = []
    obj.climate_impacts = []
    obj.origin_website = ['C3S']
    obj.language = 'en'
    obj.reindexObject()

    state = api.content.get_state(obj=obj, default="Unknown")
    if state != "published":
        print(("Object not published, publishing", obj))
        api.content.transition(obj, "publish")
    obj._p_changed = True


def save_indicator(indicator, site, data):

    print("=============================================")
    print((indicator["theme"]))

    folder_path = "en/knowledge/european-climate-data-explorer/"
    folder = site.restrictedTraverse(folder_path)

    for theme_name in indicator["theme"]:
        folder_indicator_id = theme_name.lower().replace(" ", "-")
        if folder_indicator_id not in folder.contentIds():
            print(("Create indicator folder", theme_name))
            folder_indicator = createContentInContainer(
                folder, "Folder", title=theme_name
            )

            folder_indicator.manage_addProperty(
                id="layout", value="c3s_indicators_listing", type="string"
            )
            api.content.transition(folder_indicator, "publish")
            folder_indicator._p_changed

    portal_catalog = site.portal_catalog
    brains = portal_catalog.unrestrictedSearchResults(
        **{
            "portal_type": "eea.climateadapt.c3sindicator",
            "c3s_identifier": indicator["identifier"],
            "path": "/cca/en"
        }
    )
    indicatorFound = False

    for brain in brains:
        obj = brain.getObject()
        try:
            if indicator["identifier"] == obj.c3s_identifier:
                indicatorFound = True
                update_object(obj, indicator)
                print("  UPDATE OBJECT")
        except Exception:
            pass
            # print("C3S Identifier NOT SET")

    if not indicatorFound:
        folder_path = "en/metadata/indicators/"
        folder = site.restrictedTraverse(folder_path)

        obj = createContentInContainer(
            # folder_indicator,
            folder,
            "eea.climateadapt.c3sindicator",
            title=indicator["page_title"],
        )

        obj.c3s_identifier = indicator["identifier"]
        update_object(obj, indicator)


def main():
    site = get_plone_site()
    data = get_source_data()
    base_folder = site["en"]["knowledge"]["european-climate-data-explorer"]
    annot = IAnnotations(base_folder)
    annot._p_changed = True
    annot["c3s_json_data"] = {"data": data, "fetched": datetime.datetime.now()}

    for indicator_identifier in data["indicators"]:
        save_indicator(data["indicators"][indicator_identifier], site, data)

    # for theme_id in data["themes"]:
    #    theme_folder = base_folder[theme_id]
    #    theme_folder.text = RichTextValue(
    #        data["themes"][theme_id]["description"]
    #    )
    #    print("Updated description for", theme_folder)

    transaction.commit()
    print(("Total items:" + str(len(data["indicators"]))))


if __name__ == "__main__":
    main()
