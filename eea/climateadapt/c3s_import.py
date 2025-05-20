import os

import transaction
from plone import api
from plone.api.env import adopt_user
from plone.app.textfield.value import RichTextValue
from Products.Five.browser import BrowserView
from zExceptions import Unauthorized
from zope.annotation.interfaces import IAnnotations


import datetime
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict


from eea.climateadapt.behaviors.aceitem import IAceItem
from eea.climateadapt.restapi.slate import iterate_children

# from plone.api.content import get_state

logger = logging.getLogger("eea.climateadapt")

env = os.environ.get
TRANSLATION_AUTH_TOKEN = env("TRANSLATION_AUTH_TOKEN", "")


logger = logging.getLogger("eea.climateadapt")
logging.basicConfig()

# SOURCE_URL = (
#     "https://raw.githubusercontent.com/bopen/c3s-430a-portal/"
#     "static-generator-uncached/data/data_consolidated.json"
# )

SOURCE_URL = (
    "https://raw.githubusercontent.com/bopen/c3s-430a-portal/"
    "static-generator-acceptance/data/data_consolidated.json"
)
# SOURCE_URL = "https://raw.githubusercontent.com/bopen/c3s-430a-portal/static-generator-uncached/data/data_consolidated.json"


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
    obj.description = ""
    obj.definition_app = RichTextValue(indicator["description_vis_nav"])

    if isinstance(indicator["theme"], list):
        obj.c3s_theme = indicator["theme"]
    else:
        obj.c3s_theme = [indicator["theme"]]

    obj.c3s_identifier = indicator.get("identifier", "")
    obj.overview_app_ecde_identifier = indicator.get("ecde_identifier", "")
    print(("ECDE identifier", obj.overview_app_ecde_identifier))

    if len(obj.overview_app_ecde_identifier):
        obj.overview_app_toolbox_url_v2 = indicator["detail"]
    else:
        obj.overview_app_toolbox_url = indicator["detail"]
        obj.overview_app_parameters = indicator.get("overview", "")
    print(("overview_app_toolbox_url", obj.overview_app_toolbox_url))
    print(("overview_app_parameters", obj.overview_app_parameters))
    print(("overview_app_toolbox_url v2", obj.overview_app_toolbox_url_v2))

    obj.sectors = []
    obj.climate_impacts = []
    obj.origin_website = ["C3S"]
    obj.language = "en"
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
            "path": "/cca/en",
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


def c3s_import(site):
    # import pdb
    # pdb.set_trace()

    site = api.portal.get()
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


class C3sImportView(BrowserView):
    def __call__(self):
        c3s_import(self.context)
        return "ok"


class C3sImportTriggerView(BrowserView):
    def __call__(self):
        token = self.request.getHeader("Authentication")
        if token != TRANSLATION_AUTH_TOKEN:
            raise Unauthorized

        with adopt_user(username="admin"):
            compute_broken_links(self.context)

        return "ok"
