# -*- coding: utf-8 -*-
import csv
import json
import logging
from eea.climateadapt.blocks import BlocksTraverser
import urlparse
from datetime import date
from datetime import datetime

import transaction
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from eea.climateadapt.vocabulary import _health_impacts
from plone import api
from plone.api import portal
from plone.api.portal import get_tool
from plone.api.content import get_state
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from Products.Five.browser import BrowserView
from z3c.relationfield import RelationValue
from zc.relation.interfaces import ICatalog
from plone.app.multilingual.manager import TranslationManager


from eea.climateadapt.vocabulary import BIOREGIONS
from eea.climateadapt.vocabulary import SUBNATIONAL_REGIONS

from eea.climateadapt.browser.migration_data.adaptationoption import ADAPTATION_OPTION_MIGRATION_DATA
from eea.climateadapt.browser.migration_data.adaptationoption import MAP_IPCC
from eea.climateadapt.vocabulary import _ipcc_category, _key_type_measures
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# from pkg_resources import resource_filename
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


class UpdateMissionFundingLayout(BrowserView):
    """Update volto layout of existing Mission Funding content types"""
    template = ViewPageTemplateFile('pt/migrate_mission_funding_layout.pt')

    def __call__(self):
        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog.searchResults(portal_type='mission_funding_cca')
        # fpath = resource_filename(
        #     "eea.climateadapt.behaviors", "volto_layout_missionfunding.json"
        # )
        # layout = json.load(open(fpath))

        def visitor(block):
            eu_funding_field = {
                "@id": "9bc8986e-d885-49d4-b56e-a806ebc10ec1",
                "field": {
                    "id": "is_eu_funded",
                    "title": "EU funding",
                    "widget": "boolean"
                },
                "showLabel": True
            }
            if block.get('@type') == 'metadataSection':
                fields = block.get('fields', [])
                if fields and fields[0]['field']['id'] == 'regions':
                    block['fields'] = [eu_funding_field] + fields
                    return True

        response = []
        for brain in brains:
            obj = brain.getObject()
            traverser = BlocksTraverser(obj)
            traverser(visitor)

            # obj.blocks = layout["blocks"]
            # obj.blocks_layout = layout["blocks_layout"]
            # obj.reindexObject()
            logger.info("Updated layout for %s" % obj.absolute_url())
            response.append(
                {"title": obj.title, "url": obj.absolute_url()})
            # try:
            # except Exception as e:
            #     logger.error("Failed to update %s: %s", brain.getURL(), e)

        self.results = response
        return self.template()


class DeleteCityProfileItems(BrowserView):
    """ see #261751 """

    def __call__(self):
        catalog = get_tool("portal_catalog")
        content_type = "eea.climateadapt.city_profile"
        items = [b.getObject() for b in catalog(portal_type=content_type)]

        for item in items:
            try:
                logger.info("Deleting... %s" % item.absolute_url())
                api.content.delete(item)
            except Exception:
                logger.info("Error %s" % item.absolute_url())

        return "Done"


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
                logger.info("Migrated site origin : %s %s",
                            brain.getURL(), obj.origin_website)

            elif origin_website and isinstance(origin_website, str):
                obj.origin_website = [origin_website]
                logger.info("Migrated site origin : %s %s",
                            brain.getURL(), obj.origin_website)

            elif origin_website is None:
                obj.origin_website = []
                logger.info("Migrated site origin : %s %s",
                            brain.getURL(), obj.origin_website)

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


class CountryUK:
    """Change country code from UK to GB"""

    def list(self):
        catalog = api.portal.get_tool("portal_catalog")
        res = []

        i = 0
        for _type in DB_ITEM_TYPES:
            i += 1
            if i % 100 == 0:
                transaction.savepoint()

            brains = catalog.searchResults(
                {'portal_type': _type, 'path': '/cca', 'review_state': 'published'})

            for brain in brains:
                obj = brain.getObject()

                if hasattr(obj, "geochars") and obj.geochars:
                    geochars_data = json.loads(obj.geochars)
                    if 'countries' not in geochars_data['geoElements']:
                        continue
                    countries = geochars_data['geoElements']['countries']
                    if 'UK' in countries:
                        countries.remove('UK')
                        if 'GB' not in countries:
                            countries.append(u'GB')
                        geochars_data['geoElements']['countries'] = countries
                        obj.geochars = json.dumps(geochars_data).encode()
                        obj._p_changed = True
                        logger.info(
                            "Migrated UK Countries for obj: %s", brain.getURL())

                        res.append(
                            {
                                # "title": obj.title,
                                "id": brain.UID,
                                "url": brain.getURL(),
                                # "countries": ', '.join(countries),
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
                    logger.info("Migrated health impact for obj: %s %s",
                                brain.getURL(), obj.health_impacts)

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
            logger.info("Migrated funding programme for obj: %s",
                        obj.absolute_url())

        return response


def extract_vals(val):
    """ Extract values for transnational regions, from csv row value
    """
    # Eliminate extra spaces and ,
    new_val = val.replace(" \n", "\n").replace(",", "").lstrip().rstrip()
    # Eliminate invalid values
    invalid = ['', '103', 'New region', 'Delete regions']
    # Fix some values to match the existing correct values
    correct = {
        'Alpine space': 'Alpine Space',
        'Adriatic-Ionian Region': 'Adriatic-Ionian',
        'Mediterranean Region': 'Mediterranean',
        'Mediterranean sea basin': 'Mediterranean Sea Basin',
        'Adriatic Ionian': 'Adriatic-Ionian',
        'Baltic': 'Baltic Sea',
    }
    new_values = []
    for a_val in new_val.split("\n"):
        if a_val not in invalid:
            new_value = correct.get(a_val, a_val)
            if new_value == 'Northern Periphery and Arctic':
                new_values.append('Northern Periphery')
                new_values.append('Arctic')
            else:
                new_values.append(new_value)
    return new_values


def extract_subnational_vals(val):
    """ Extract values for subnational regions, from csv row value
    """
    # Eliminate extra spaces and ,
    new_val = val.replace(" \n", "\n").replace(",", "").lstrip().rstrip()
    # Eliminate invalid values
    invalid = ['', '-', 'Nuts 2']
    # Fix some values to match the existing correct values
    correct = {
        'ITI17 - Tuscany': 'Toscana (IT)',
        'Pisa (Italy)': 'Pisa (IT)',
    }
    new_values = []
    for a_val in new_val.split("\n"):
        if a_val not in invalid:
            new_value = a_val
            if ('SK) V' in new_value and ',' in val) or (
                    'FI) E' in new_value and ',' in val) or (
                    'any Pisa' in new_value and ',' in val):
                # Západné Slovensko (SK), Východné Slovensko (SK)
                # Pohjois- ja Itä-Suomi (FI), Etelä-Suomi (FI)
                # ITI17 - Tuscany, Pisa (Italy)
                temp = val.split(", ")
                new_values.append(correct.get(temp[0], temp[0]))
                new_values.append(correct.get(temp[1], temp[1]))
            else:
                new_values.append(correct.get(new_value, new_value))
    return new_values


def search_for(content_types=[], tag="", at_least_one=[],
               tag_is_optional=False):
    """ Search for items having the content types, the tag, and
        some optional text/tags
    """
    catalog = api.portal.get_tool('portal_catalog')
    res = {}

    if at_least_one is None:
        # do a simple query
        found = catalog.searchResults({
            'portal_type': content_types,
            'path': '/cca/en',
        })
        for brain in found:
            obj = brain.getObject()
            if obj.UID() not in res.keys():
                res[obj.UID()] = {
                    'obj': obj,
                    'reason_terms': [],
                    'reason_tags': []
                }
    else:
        # search for each term
        for text_to_search in at_least_one:
            found = catalog.searchResults({
                'portal_type': content_types,
                'path': '/cca/en',
                'SearchableText': text_to_search
            })
            for brain in found:
                obj = brain.getObject()
                if obj.UID() not in res.keys():
                    res[obj.UID()] = {
                        'obj': obj,
                        'reason_terms': [text_to_search],
                        'reason_tags': []
                    }
                else:
                    if text_to_search not in res[obj.UID()]['reason_terms']:
                        res[obj.UID()]['reason_terms'].append(text_to_search)

    if tag_is_optional is True:
        # TODO search for more content based only on this tag?
        pass
    else:
        # use the tag as a filter for items found above
        temp = res
        res = {}

        for item_id in temp.keys():
            item = temp[item_id]
            obj = item['obj']

            try:
                old_values = []
                values = json.loads(obj.geochars)[
                    'geoElements']['macrotrans']
                for value in values:
                    bio = BIOREGIONS.get(value, None)
                    if bio is None:
                        logger.info("Missing bioregion: %s", value)
                    else:
                        old_values.append(bio)
            except Exception as err:
                old_values = []

            if tag in old_values:
                item['reason_tags'].append(tag)
                res[obj.UID()] = item

    return res


def justify_migration(objs={}, action=""):
    """ Human readable explanation of modified objects
    """
    res = []
    for item_id in objs.keys():
        item = objs[item_id]
        obj = item['obj']
        logger.info("----------------------")
        logger.info(obj.absolute_url())
        logger.info(action)
        reason = "Found terms {0}, Found tags: {1}".format(
            item['reason_terms'], item['reason_tags']
        )
        logger.info(reason)
        res.append({
            'URL': obj.absolute_url(),
            'action': action,
            'reason': reason
        })
    return res


def migrate_delete_tag(objs=[], tag=""):
    """ Update the list of objects deleting the new macro transnational region
        tag in obj.geochars['geoElements']['macrotrans']

        Do the same for their translated items
    """
    regions = {}
    for k, v in BIOREGIONS.items():
        if 'TRANS_MACRO' in k:
            regions[v] = k

    for item_id in objs.keys():
        item = objs[item_id]
        obj = item['obj']
        try:
            old_values = []
            values = json.loads(obj.geochars)['geoElements']['macrotrans']
            for value in values:
                bio = BIOREGIONS.get(value, None)
                if bio is None:
                    logger.info("Missing bioregion: %s", value)
                else:
                    old_values.append(bio)
        except Exception as err:
            old_values = []
            logger.info(err)

        logger.info("---------------------------------------- Migrating:")
        logger.info(obj.absolute_url())
        logger.info(obj.geochars)
        logger.info(old_values)
        logger.info("Reason terms: %s", item['reason_terms'])
        logger.info("Reason tags: %s", item['reason_tags'])

        # Set new geochars
        new_values = []

        for val in old_values:
            if val not in new_values and val != tag:
                new_values.append(val)

        try:
            new_geochars = json.loads(obj.geochars)
        except Exception:
            new_geochars = {'geoElements': {}}

        macro = []
        new_macros = new_values
        for new_macro in new_macros:
            if new_macro in regions:
                macro.append(regions[new_macro])
            else:
                logger.info("------------- MISSING: %s", new_macro)

        new_geochars['geoElements']['macrotrans'] = macro
        logger.info("=== NEW: %s", new_geochars)

        prepared_val = json.dumps(new_geochars).encode()
        obj.geochars = prepared_val
        obj._p_changed = True
        obj.reindexObject()

        # Apply the same change for translated content
        try:
            translations = TranslationManager(obj).get_translations()
        except Exception:
            translations = None

        if translations is not None:
            for language in translations.keys():
                trans_obj = translations[language]
                trans_obj.geochars = prepared_val
                trans_obj._p_changed = True
                trans_obj.reindexObject()
                logger.info("Migrated too: %s",
                            trans_obj.absolute_url())


def migrate_add_tag(objs=[], tag=""):
    """ Update the list of objects adding the new macro transnational region
        tag in obj.geochars['geoElements']['macrotrans']

        Do the same for their translated items
    """
    regions = {}
    for k, v in BIOREGIONS.items():
        if 'TRANS_MACRO' in k:
            regions[v] = k

    for item_id in objs.keys():
        item = objs[item_id]
        obj = item['obj']
        try:
            old_values = []
            values = json.loads(obj.geochars)['geoElements']['macrotrans']
            for value in values:
                bio = BIOREGIONS.get(value, None)
                if bio is None:
                    logger.info("Missing bioregion: %s", value)
                else:
                    old_values.append(bio)
        except Exception as err:
            old_values = []
            logger.info(err)

        logger.info("---------------------------------------- Migrating:")
        logger.info(obj.absolute_url())
        logger.info(obj.geochars)
        logger.info(old_values)
        logger.info("Reason terms: %s", item['reason_terms'])
        logger.info("Reason tags: %s", item['reason_tags'])

        # Set new geochars
        new_values = []
        new_values.append(tag)

        for val in old_values:
            if val not in new_values:
                new_values.append(val)

        try:
            new_geochars = json.loads(obj.geochars)
        except Exception:
            new_geochars = {'geoElements': {}}

        macro = []
        new_macros = new_values
        for new_macro in new_macros:
            if new_macro in regions:
                macro.append(regions[new_macro])
            else:
                logger.info("------------- MISSING: %s", new_macro)

        new_geochars['geoElements']['macrotrans'] = macro
        logger.info("=== NEW: %s", new_geochars)

        prepared_val = json.dumps(new_geochars).encode()
        obj.geochars = prepared_val
        obj._p_changed = True
        obj.reindexObject()

        # Apply the same change for translated content
        try:
            translations = TranslationManager(obj).get_translations()
        except Exception:
            translations = None

        if translations is not None:
            for language in translations.keys():
                trans_obj = translations[language]
                trans_obj.geochars = prepared_val
                trans_obj._p_changed = True
                trans_obj.reindexObject()
                logger.info("Migrated too: %s",
                            trans_obj.absolute_url())


class MigrateAdaptationOptionItems(BrowserView):
    """
    Refs #254130 -> Adaptation options_KTM_IPCC_for retagging.xlsx
                    KTM and IPCC categories
    """

    def find_adaptationoption_item(self, item_title):
        """ Get the item having the title
        """
        content_type = "eea.climateadapt.adaptationoption"
        res = api.content.find(portal_type=content_type, Title=item_title)
        if len(res) == 0:
            return None
        else:
            return res[0].getObject()

    def __call__(self):
        logs = []

        for csv_line in ADAPTATION_OPTION_MIGRATION_DATA.splitlines():
            if len(csv_line) > 2:
                csv_list = csv.reader([csv_line])
                data_row = next(csv_list)
                item_title = data_row[0]
                res = self.find_adaptationoption_item(item_title)
                logger.info("Migrating... " + item_title)
                if res is None:
                    logger.warning("Item not found.")
                    log_info = {
                        "title": item_title,
                        "url": "ITEM NOT FOUND",
                    }
                else:
                    item = res

                    ktm = []
                    ipcc = []
                    for index, value in enumerate(data_row):
                        if value == "X":

                            if index <= len(_key_type_measures):
                                to_check = _key_type_measures[index-1][0]
                                ktm.append(to_check)
                            else:
                                to_check = _ipcc_category[
                                    MAP_IPCC[index - 1 -
                                             len(_key_type_measures)]
                                ][0]
                                ipcc.append(to_check)

                    log_info = {
                        "title": item_title,
                        "url": item.absolute_url(),
                        "new ktm": ktm,
                        "new ipcc": ipcc
                    }

                    item.key_type_measures = ktm
                    item.ipcc_category = ipcc
                    item._p_changed = True
                    item.reindexObject()

                    # Apply the same change for translated content
                    try:
                        translations = TranslationManager(
                            item).get_translations()
                    except Exception:
                        translations = None

                    if translations is not None:
                        for language in translations.keys():
                            trans_obj = translations[language]
                            trans_obj.key_type_measures = ktm
                            trans_obj.ipcc_category = ipcc
                            trans_obj._p_changed = True
                            trans_obj.reindexObject()
                            logger.info("Migrated too: %s",
                                        trans_obj.absolute_url())

                logs.append(log_info)

        report = logs
        json_object = json.dumps(report, indent=4)
        r_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open("/tmp/migration_report_" + r_date + ".json", "w") as outf:
            outf.write(json_object)

        return "Done"


class MigrateTransnationalRegionsDatabaseItems(BrowserView):
    """
    Refs #254130 Step 3.2:
    IF database item
    AND Arctic
        => ADD Northern Periphery and Arctic

    AND Black Sea
        => ADD Black Sea basin (NEXT)

    => REMOVE:
        Balkan-Mediterranean
        Mid-Atlantic
        Arctic
        Southeast
        Black Sea

    AND Amazonia or Caribbean Area or Indian Ocean Area
        => ADD Outermost regions

    => REMOVE: Amazonia, Caribbean Area, Indian Ocean Area
    """

    def __call__(self):
        content_types = [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.tool",
            "eea.climateadapt.video",
        ]

        logs = []

        # ADD Northern Periphery and Arctic ----------------------------- 3. 2.
        found_items = search_for(
            content_types=content_types,
            tag="Arctic",
            at_least_one=None,
            tag_is_optional=False)

        logs += justify_migration(
            objs=found_items,
            action="Add tag: Northern Periphery and Arctic")
        migrate_add_tag(objs=found_items, tag="Northern Periphery and Arctic")

        # ADD Black Sea Basin (NEXT) ------------------------------------ 3. 2.
        found_items = search_for(
            content_types=content_types,
            tag="Black Sea",
            at_least_one=None,
            tag_is_optional=False)

        logs += justify_migration(
            objs=found_items,
            action="Add tag: Black Sea Basin (NEXT)")
        migrate_add_tag(objs=found_items, tag="Black Sea Basin (NEXT)")

        # DELETE tags --------------------------------------------------- 3. 3.
        delete_tags = ["Balkan-Mediterranean", "Mid-Atlantic",
                       "Arctic", "South East Europe", "Black Sea"]
        for a_tag in delete_tags:
            found_items = search_for(
                content_types=content_types,
                tag=a_tag,
                at_least_one=None,
                tag_is_optional=False)

            action = "Delete tag: " + a_tag
            logs += justify_migration(objs=found_items, action=action)
            migrate_delete_tag(objs=found_items, tag=a_tag)

        # ADD Outermost Regions ----------------------------------------- 3. 4.
        found_items = search_for(
            content_types=content_types,
            tag="Amazonia",
            at_least_one=None,
            tag_is_optional=False)

        logs += justify_migration(
            objs=found_items,
            action="Add tag: Outermost Regions")
        migrate_add_tag(objs=found_items, tag="Outermost Regions")

        # ADD Outermost Regions ----------------------------------------- 3. 4.
        found_items = search_for(
            content_types=content_types,
            tag="Caribbean Area",
            at_least_one=None,
            tag_is_optional=False)

        logs += justify_migration(
            objs=found_items,
            action="Add tag: Outermost Regions")
        migrate_add_tag(objs=found_items, tag="Outermost Regions")

        # ADD Outermost Regions ----------------------------------------- 3. 4.
        found_items = search_for(
            content_types=content_types,
            tag="Indian Ocean Area",
            at_least_one=None,
            tag_is_optional=False)

        logs += justify_migration(
            objs=found_items,
            action="Add tag: Outermost Regions")
        migrate_add_tag(objs=found_items, tag="Outermost Regions")

        # DELETE tags --------------------------------------------------- 3. 4.
        delete_tags = ["Amazonia", "Caribbean Area", "Indian Ocean Area"]
        for a_tag in delete_tags:
            found_items = search_for(
                content_types=content_types,
                tag=a_tag,
                at_least_one=None,
                tag_is_optional=False)

            action = "Delete tag: " + a_tag
            logs += justify_migration(objs=found_items, action=action)
            migrate_delete_tag(objs=found_items, tag=a_tag)

        report = logs
        json_object = json.dumps(report, indent=4)
        r_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open("/tmp/migration_report_" + r_date + ".json", "w") as outf:
            outf.write(json_object)

        return "Done"


class MigrateTransnationalRegionsDatabaseItemsOld(BrowserView):
    """ Update transnational regions

    --- The request simplified - -----------------------------------------------
    ** If we replace with a single tag, the first replace will be lost. So,
    instead of REPLACE we will ADD the new tag then the old Balkan-M will be
    deleted for all. This way Balkan-M + Greece = > Mediterranean AND also
    Balkan-M + Greece = > Adriatic-I Region.

    IF content_types
    AND Balkan-Mediterranean
    IF Greece
     OR Albania
      OR Macedonia
       OR Bulgaria
         = > REPLACE Balkan-Mediterranean WITH Mediterranean **

        IF Greece
        OR Albania
        OR Macedonia
         = > REPLACE Balkan-Mediterranean WITH Adriatic-Ionian Region      **

        IF Bulgaria
         = > REPLACE Balkan-Mediterranean WITH Danube Region               **

        IF countries not mentioned
         = > DELETE tag Balkan-Mediterranean

    AND Mediterranean
    IF Egypt
     OR Tunisia
      OR Algeria
       OR Turkey
        OR Israel
        OR Lebanon
        OR Palestine
        OR Jordan
        OR "Southern and Eastern Mediterranean Countries"
        OR "surrounding regions"
        OR "Africa"
        OR "African"
        OR "Mediterranean basin"
        OR "Mediterranean Sea basin".
         = > ADD tag MEDITERRANEAN SEA BASIN

    AND Danube Area
    IF Black Sea
         = > ADD tag Black Sea Basin

    AND South East Europe
    IF Morocco
     OR Africa
      OR Canary
         = > ADD tag Mid-Atlantic

    --- The request - ----------------------------------------------------------
    ALL database items EXCEPT: case studies, indicators, adaptation options
    a. For the items that are currently tagged for Balkan Mediterranean region:
        REPLACE THE  TAG "Balkan-Mediterranean" WITH
        i. MEDITERRANEAN tag(items with the following countries selected
                             or mentioned in the text:
                             Greece OR Albania OR Macedonia OR Bulgaria)
        ii. ADRIATIC-IONIAN REGION  tag(items with the following
                                        countries selected or mentioned in the text:
                                        Greece OR Albania OR Macedonia)
        iii. DANUBE REGION tag(items with Bulgaria selected or mentioned)
        iv. NOTHING(DELETE tag) if countries are not mentioned

    b. For the items  that are currently tagged for Mediterranean region:
        i. ADD THE TAG MEDITERRANEAN SEA BASIN
        (NEW TAG needs to be created first) IF the items include or mention:
        Egypt OR Tunisia OR Algeria OR Turkey OR Israel OR Lebanon OR
        Palestine OR Jordan OR "Southern and Eastern Mediterranean Countries"
        OR "surrounding regions" OR "Africa" OR "African" or
        "Mediterranean basin" OR "Mediterranean Sea basin".

    c. For the items that are currently tagged for Danube Area
    i. ADD the tag "Black Sea Basin" (NEW TAG needs to be created first)
     if they mention "Black Sea"

    d. For the items that are currently tagged for South East Europe
    i. ADD the tag "Mid-Atlantic" (NEW TAG needs to be created first)
     IF the item include or mention "Morocco" OR "Africa" OR "Canary"
      Note. No items are currently found with these words
    """

    def __call__(self):
        return
        content_types = [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.tool",
            "eea.climateadapt.video",
        ]

        logs = []

        # ADD Mediterranean --------------------------------------------- a. i.
        found_items = search_for(
            content_types=content_types,
            tag="Balkan-Mediterranean",
            at_least_one=["Greece", "Albania", "Macedonia", "Bulgaria"],
            tag_is_optional=False)

        logs += justify_migration(objs=found_items,
                                  action="Add tag: Mediterranean")
        migrate_add_tag(objs=found_items, tag="Mediterranean")

        # ADD Adriatic-Ionian ------------------------------------------ a. ii.
        found_items = search_for(
            content_types=content_types,
            tag="Balkan-Mediterranean",
            at_least_one=["Greece", "Albania", "Macedonia"],
            tag_is_optional=False)

        logs += justify_migration(objs=found_items,
                                  action="Add tag: Adriatic-Ionian")
        migrate_add_tag(objs=found_items, tag="Adriatic-Ionian")

        # ADD Danube -------------------------------------------------- a. iii.
        found_items = search_for(
            content_types=content_types,
            tag="Balkan-Mediterranean",
            at_least_one=["Bulgaria"],
            tag_is_optional=False)

        logs += justify_migration(objs=found_items,
                                  action="Add tag: Danube")
        migrate_add_tag(objs=found_items, tag="Danube")

        # DELETE Balkan-Mediterranean ---------------------------------- a. iv.
        found_items = search_for(
            content_types=content_types,
            tag="Balkan-Mediterranean",
            at_least_one=None,
            tag_is_optional=False)

        logs += justify_migration(objs=found_items,
                                  action="Delete tag: Balkan-Mediterranean")
        migrate_delete_tag(objs=found_items, tag="Balkan-Mediterranean")

        # ADD Mediterranean Sea Basin ----------------------------------- b. i.
        found_items = search_for(
            content_types=content_types,
            tag="Mediterranean",
            at_least_one=[
                "Egypt", "Tunisia", "Algeria", "Turkey", "Israel",
                "Lebanon", "Palestine", "Jordan",
                "Southern and Eastern Mediterranean Countries",
                "surrounding regions", "Africa", "African",
                "Mediterranean basin", "Mediterranean Sea basin"],
            tag_is_optional=False)

        logs += justify_migration(objs=found_items,
                                  action="Add tag: Mediterranean Sea Basin")
        migrate_add_tag(objs=found_items, tag="Mediterranean Sea Basin")

        # ADD Black Sea Basin ------------------------------------------- c. i.
        found_items = search_for(
            content_types=content_types,
            tag="Danube",
            at_least_one=["Black Sea"],
            tag_is_optional=False)

        logs += justify_migration(objs=found_items,
                                  action="Add tag: Black Sea Basin")
        migrate_add_tag(objs=found_items, tag="Black Sea Basin")

        # ADD Mid-Atlantic ---------------------------------------------- d. i.
        found_items = search_for(
            content_types=content_types,
            tag="South East Europe",
            at_least_one=["Morocco", "Africa", "Canary"],
            tag_is_optional=False)

        logs += justify_migration(objs=found_items,
                                  action="Add tag: Mid-Atlantic")
        migrate_add_tag(objs=found_items, tag="Mid-Atlantic")

        report = logs
        json_object = json.dumps(report, indent=4)
        r_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open("/tmp/migration_report_" + r_date + ".json", "w") as outf:
            outf.write(json_object)

        return "Done"


class MigrateTransnationalRegionsIndicators(BrowserView):
    """ Database INDICATORS(that are always tagged for all regions)
    a. Remove Balkan-Mediterranean tag for all the items
     b. Add Black Sea Basin, Mediterranean Sea Basin, Mid-Atlantic
      (3 new tags need to be created FIRST) for all the items
    """

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(
            path='/cca/en',
            portal_type="eea.climateadapt.indicator")

        regions = {}
        for k, v in BIOREGIONS.items():
            if 'TRANS_MACRO' in k:
                regions[v] = k

        logs = []
        with_empty_field = 0
        with_values = 0
        for brain in brains:
            obj = brain.getObject()
            try:
                old_values = []
                values = json.loads(obj.geochars)['geoElements']['macrotrans']
                for value in values:
                    bio = BIOREGIONS.get(value, None)
                    if bio is None:
                        logger.info("Missing bioregion: %s", value)
                    else:
                        old_values.append(bio)
            except Exception as err:
                old_values = []
                # logger.info(err)

            logger.info("---------------------------------------- Migrating:")
            logger.info(obj.absolute_url())
            logger.info(obj.geochars)
            logger.info(old_values)
            if len(old_values) == 0:
                with_empty_field += 1
            else:
                with_values += 1

            # Set new geochars
            new_values = []
            include_vals = ["Black Sea Basin", "Mediterranean Sea Basin",
                            "Mid-Atlantic"]
            exclude_vals = ["Balkan-Mediterranean"]

            for val in include_vals:
                new_values.append(val)

            for val in old_values:
                if val not in new_values and val not in exclude_vals:
                    new_values.append(val)

            try:
                new_geochars = json.loads(obj.geochars)
            except Exception:
                new_geochars = {'geoElements': {}}

            macro = []
            new_macros = new_values
            for new_macro in new_macros:
                if new_macro in regions:
                    macro.append(regions[new_macro])
                else:
                    logger.info("------------- MISSING: %s", new_macro)

            new_geochars['geoElements']['macrotrans'] = macro
            logger.info("=== NEW: %s", new_geochars)

            if len(old_values) > 0:
                prepared_val = json.dumps(new_geochars).encode()
                obj.geochars = prepared_val
                obj._p_changed = True
                obj.reindexObject()

                logs.append({
                    'url': obj.absolute_url(),
                    'action': 'Geochars: Add:{0} Delete:{1}.'.format(
                        include_vals, exclude_vals
                    )
                })

                # Apply the same change for translated content
                try:
                    translations = TranslationManager(obj).get_translations()
                except Exception:
                    translations = None

                if translations is not None:
                    for language in translations.keys():
                        trans_obj = translations[language]
                        trans_obj.geochars = prepared_val
                        trans_obj._p_changed = True
                        trans_obj.reindexObject()
                        logger.info("Migrated too: %s",
                                    trans_obj.absolute_url())

        logger.info("With empty field %s", with_empty_field)
        logger.info("With values %s", with_values)

        report = logs
        json_object = json.dumps(report, indent=4)
        r_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open("/tmp/migration_report_" + r_date + ".json", "w") as outf:
            outf.write(json_object)
        return "Done"


class CaseStudies:
    """Migrate case studies
    Use Excel file - column AN, to retag case studies.
     The column AN list the transnational regions to be displayed
      on-line in each case study.
       https: // taskman.eionet.europa.eu/issues/156654  # note-2
    """

    def list(self):
        response = []
        fileUploaded = self.request.form.get("fileToUpload", None)

        if not fileUploaded:
            return response

        reader = csv.reader(
            fileUploaded,
            delimiter=",",
            quotechar='"',
            # dialect='excel',
        )

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(
            path='/cca/en',
            portal_type="eea.climateadapt.casestudy")

        case_studies = [b.getObject() for b in brains]
        items = {}
        for case_study in case_studies:
            items[case_study.title] = case_study

        items_new = {}
        for case_study in reader:
            items_new[case_study[2].decode('utf-8')] = {
                'trans_macro': case_study[39].decode('utf-8'),
                'subnational': case_study[34].decode('utf-8'),
            }

        new_not_found = []
        for x in items_new.keys():
            if x not in items.keys():
                new_not_found.append(x)

        old_not_found = []
        old_not_found_urls = []
        for x in items.keys():
            if x not in items_new.keys():
                old_not_found.append(x)
                not_found_obj = items[x]
                if get_state(not_found_obj) not in ['archived', 'private']:
                    old_not_found_urls.append(not_found_obj.absolute_url())

        logger.info("Case studies not found in csv file: %s", old_not_found)
        logger.info("Case studies to be verified by URLs: %s",
                    old_not_found_urls)
        logger.info("Case studies not found in database: %s", new_not_found)

        regions = {}
        for k, v in BIOREGIONS.items():
            if 'TRANS_MACRO' in k:
                regions[v] = k

        sub_regions = {}
        for k, v in SUBNATIONAL_REGIONS.items():
            if 'SUBN_' in k:
                sub_regions[v] = k

        list_new_values = []
        list_new_sub_values = []

        for item in items_new.keys():
            new_values = extract_vals(items_new[item]['trans_macro'])
            new_sub_values = extract_subnational_vals(
                items_new[item]['subnational'])

            for a_val in new_values:
                list_new_values.append(a_val)
            for a_sub_val in new_sub_values:
                list_new_sub_values.append(a_sub_val)

            case_study = items.get(item, None)
            if case_study is not None:
                logger.info("Migrate %s", case_study.absolute_url())
                try:
                    old_values = []
                    values = json.loads(case_study.geochars)[
                        'geoElements']['macrotrans']
                    for value in values:
                        bio = BIOREGIONS.get(value, None)
                        if bio is None:
                            logger.info("Missing bioregion: %s", value)
                        else:
                            old_values.append(bio)
                except Exception:
                    old_values = None

                # Set new geochars
                try:
                    new_geochars = json.loads(case_study.geochars)
                except Exception:
                    new_geochars = {'geoElements': {}}

                logger.info("=== OLD: %s", new_geochars)
                macro = []
                new_macros = new_values
                for new_macro in new_macros:
                    if new_macro in regions:
                        macro.append(regions[new_macro])
                    else:
                        logger.info("------------- MISSING: %s", new_macro)

                sub_val = []
                for new_sub in new_sub_values:
                    encoded_sub = new_sub.encode('utf-8')
                    if encoded_sub in sub_regions:
                        sub_val.append(sub_regions[encoded_sub])
                    else:
                        logger.info("------------- MISSING: %s", new_sub)
                new_geochars['geoElements']['macrotrans'] = macro
                new_geochars['geoElements']['subnational'] = sub_val
                logger.info("=== NEW: %s", new_geochars)

                # Subnational regions
                try:
                    old_sub_values = []
                    sub_values = json.loads(case_study.geochars)[
                        'geoElements']['subnational']
                    for sub_value in sub_values:
                        # Some keys are non-ASCII, so we use encoding:
                        # (Pdb) sub_values
                        # [u'SUBN_Catalu\xf1a__ES_']
                        # (Pdb) SUBNATIONAL_REGIONS[sub_values[0]]
                        # *** KeyError: u'SUBN_Catalu\xf1a__ES_'
                        # (Pdb) SUBNATIONAL_REGIONS[
                        #                      sub_values[0].encode('utf-8')]
                        # 'Catalu\xc3\xb1a (ES)'
                        sub = SUBNATIONAL_REGIONS.get(
                            sub_value.encode('utf-8'), None)

                        if sub is None:
                            logger.info("Missing subnational: %s", sub_value)
                        else:
                            old_sub_values.append(sub)
                except Exception:
                    old_sub_values = None

                prepared_val = json.dumps(new_geochars).encode()
                obj = case_study
                obj.geochars = prepared_val
                obj._p_changed = True
                obj.reindexObject()

                # Apply the same change for translated content
                try:
                    translations = TranslationManager(obj).get_translations()
                except Exception:
                    translations = None

                if translations is not None:
                    for language in translations.keys():
                        trans_obj = translations[language]
                        trans_obj.geochars = prepared_val
                        trans_obj._p_changed = True
                        trans_obj.reindexObject()
                        logger.info("Migrated too: %s",
                                    trans_obj.absolute_url())

                logger.info("OLD values: %s", old_values)
                logger.info("NEW values: %s", new_values)
            else:
                logger.info("Not found: %s", item)

        # Make sure all values are defined in our vocabulary
        missing_definitions = [x for x in set(
            list_new_values) if x not in BIOREGIONS.values()]
        logger.info("Values to be added in BIOREGIONS definition: %s",
                    missing_definitions)
        missing_sub_definitions = [x for x in set(
            list_new_sub_values) if x.encode(
                'utf-8') not in SUBNATIONAL_REGIONS.values()]
        logger.info("Values to be added in SUBNATIONAL definition: %s",
                    missing_sub_definitions)

        logger.info("DONE")
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
            'Copernicus Climate Change Service - Climate-ADAPT (europa.eu)':
                {'url': 'copernicus-climate-change-service-ecmw',
                    'id': 0, 'object': None},
            'European Centre for Disease Prevention and Control - Climate-ADAPT (europa.eu)':
                {'url': 'european-centre-for-disease-prevention-and-control-ecdc',
                    'id': 0, 'object': None},
            'European Commission - Climate-ADAPT (europa.eu)':
                {'url': 'european-commission', 'id': 0, 'object': None},
            'European Environment Agency - Climate-ADAPT (europa.eu)':
                {'url': 'european-environment-agency-eea', 'id': 0, 'object': None},
            'European Food Safety Authority - Climate-ADAPT (europa.eu)':
                {'url': 'european-food-safety-authority', 'id': 0, 'object': None},
            'Lancet Countdown - Climate-ADAPT (europa.eu)':
                {'url': 'lancet-countdown', 'id': 0, 'object': None},
            'World Health Organization - Regional Office for Europe - Climate-ADAPT (europa.eu)':
                {'url': 'who-regional-office-for-europe-who-europe',
                    'id': 0, 'object': None},
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
                map_organisations[title]['id'] = util.getId(
                    orgs[0].getObject())
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

            if len(item['partners']) < 5:
                continue

            if item['partners'] == 'Other Organisations':
                continue

            item['partners'] = item['partners'].replace('\xe2\x80\x94', '-')

            obj = self.get_object(item['url'])

            if not obj:
                logger.warning("Object not found: %s", item['url'])
                continue

            if item['partners'] not in map_organisations:
                logger.warning(
                    "Partner not found: %s [%s]", item['url'], item['partners'])
                continue

            partner_object_id = map_organisations[item['partners']]['id']
            if not partner_object_id:
                logger.warning(
                    "Partner not match: %s [%s]", item['url'], item['partners'])
                continue

            obj.contributor_list = []

            logger.info("Partner set: %s [%s]", item['url'], item['partners'])
            obj.contributor_list.append(RelationValue(partner_object_id))
            obj._p_changed = True
            notify(ObjectModifiedEvent(obj))

            # transaction.savepoint()
            response.append({
                'title': obj.title,
                'url': item['url'],
                'partners': item['partners'],
            })

        return response


class MoveContributorsToList:

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

                if hasattr(obj, "contributors"):
                    if obj.contributors:
                        obj.contributor_list = obj.contributors
                        delattr(obj, 'contributors')
                        obj._p_changed = True

                    logger.info(
                        "Migrated contributors for obj: %s", brain.getURL())

                    res.append(
                        {
                            "title": obj.title,
                            "id": brain.UID,
                            "url": brain.getURL()
                        }
                    )

        return res


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

                    response.append(
                        {"title": obj.title, "url": brain.getURL()})
                    logger.info("Organisation logo: %s", brain.getURL())

        logger.info("Articles with logo in response: %s", len(response))
        return response


class SourceToRichText:
    """Migrate funding_programme field"""

    def list(self):
        catalog = api.portal.get_tool("portal_catalog")

        DB_ITEM_TYPES = [
            "eea.climateadapt.adaptationoption",
            # "eea.climateadapt.casestudy",
            # "eea.climateadapt.guidancedocument",
            # "eea.climateadapt.indicator",
            # "eea.climateadapt.informationportal",
            # "eea.climateadapt.organisation",
            # "eea.climateadapt.publicationreport",
            # "eea.climateadapt.tool",
            # "eea.climateadapt.video"
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
                    logger.info("Migrated source type for obj: %s",
                                brain.getURL())


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


class UpdateHealthItemsNone:

    def list(self):
        # overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool("portal_catalog")
        res = []

        for _type in DB_ITEM_TYPES:

            brains = catalog.searchResults(portal_type=_type)

            for brain in brains:
                obj = brain.getObject()

                if hasattr(obj, "health_impacts") \
                        and obj.health_impacts \
                        and [None] == obj.health_impacts:
                    logger.info("Have none for obj: %s", brain.getURL())

                    res.append(
                        {
                            "title": obj.title,
                            "id": brain.UID,
                            "url": brain.getURL(),
                            "health_impacts": obj.health_impacts,
                        }
                    )

                    del obj.health_impacts
                    obj._p_changed = True

        return res


class AllObjectsNotify:
    """ Migrate funding_programme field
    """

    def get_object(self, path):
        local_path = path.replace('http://', '')
        local_path = local_path.replace('https://', '')

        local_path = local_path[local_path.find('/'):]
        local_path = local_path[1:]

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
            'Copernicus Climate Change Service - Climate-ADAPT (europa.eu)':
                {'url': 'copernicus-climate-change-service-ecmw',
                    'id': 0, 'object': None},
            'European Centre for Disease Prevention and Control - Climate-ADAPT (europa.eu)':
                {'url': 'european-centre-for-disease-prevention-and-control-ecdc',
                    'id': 0, 'object': None},
            'European Commission - Climate-ADAPT (europa.eu)':
                {'url': 'european-commission', 'id': 0, 'object': None},
            'European Environment Agency - Climate-ADAPT (europa.eu)':
                {'url': 'european-environment-agency-eea', 'id': 0, 'object': None},
            'European Food Safety Authority - Climate-ADAPT (europa.eu)':
                {'url': 'european-food-safety-authority', 'id': 0, 'object': None},
            'Lancet Countdown - Climate-ADAPT (europa.eu)':
                {'url': 'lancet-countdown', 'id': 0, 'object': None},
            'World Health Organization - Regional Office for Europe - Climate-ADAPT (europa.eu)':
                {'url': 'who-regional-office-for-europe-who-europe',
                    'id': 0, 'object': None},
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
                map_organisations[title]['id'] = util.getId(
                    orgs[0].getObject())
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

            if len(item['partners']) < 5:
                continue

            if item['partners'] == 'Other Organisations':
                continue

            item['partners'] = item['partners'].replace('\xe2\x80\x94', '-')

            obj = self.get_object(item['url'])

            if not obj:
                logger.warning("Object not found: %s", item['url'])
                continue

            if item['partners'] not in map_organisations:
                logger.warning(
                    "Partner not found: %s [%s]", item['url'], item['partners'])
                continue

            partner_object_id = map_organisations[item['partners']]['id']
            if not partner_object_id:
                logger.warning(
                    "Partner not match: %s [%s]", item['url'], item['partners'])
                continue

            logger.info("Notificattion set: %s", item['url'])
            notify(ObjectModifiedEvent(obj))

            # transaction.savepoint()
            response.append({
                'title': obj.title,
                'url': item['url'],
            })

        return response


class MigrateFundingProgrammeUpdates:
    def list(self):
        funding_programme_updates = {
            "Environment and climate action (LIFE)": "LIFE - Environment and climate action",
            "European earth observation programme (Copernicus)": "COPERNICUS - European earth observation programme",
            "Horizon 2020": "HORIZON 2020",
            "Interreg": "INTERREG",
            "Seventh Framework Programme (FP7: 2007-2013)": "FP7: 2007/2013 - Seventh Framework Programme",
            "Sixth Framework Programme (FP6: 2002-2006)": "FP6: 2002/2006 - Sixth Framework Programme",
            "Fifth Framework Programme (FP5: 1998-2002)": "FP5: 1998/2002 - Fifth Framework Programme"
        }

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            portal_type="eea.climateadapt.aceproject")

        res = []
        for brain in brains:
            obj = brain.getObject()

            if hasattr(obj, "funding_programme") \
                    and obj.funding_programme in funding_programme_updates:
                logger.info("Will update for: %s", brain.getURL())

                obj.funding_programme = funding_programme_updates[obj.funding_programme]
                obj._p_changed = True

            notify(ObjectModifiedEvent(obj))

            res.append(
                {
                    "title": obj.title,
                    "id": brain.UID,
                    "url": brain.getURL(),
                    "funding_programme": obj.funding_programme,
                }
            )

        return res


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

                obj.health_impacts = [health_impacts.get(
                    item["health_impact"], None)]
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


# 142756
class TransnationalRegions:
    """Update TransnationalRegions field"""

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

        regions = {}
        site = api.portal.get()
        for k, v in BIOREGIONS.items():
            if 'TRANS_MACRO' in k:
                regions[v] = k

        i_transaction = 0
        # need condition for "Yes"
        for row in reader:
            i_transaction += 1
            if i_transaction % 100 == 0:
                transaction.savepoint()
            item = {}
            item["title"] = row[0]
            item["region_old"] = row[5]
            item["region_new"] = row[6]
            item["url"] = row[11]
            # item["uid"] = row[6]

            local_path = item['url'].replace('http://', '')
            local_path = local_path.replace('https://', '')

            local_path = local_path[local_path.find('/'):]
            local_path = local_path[1:]

            try:
                obj = site.restrictedTraverse(local_path.strip())
            except Exception, e:
                obj = None

            if not obj:
                continue

            geochars = json.loads(obj.geochars)
            modified = False

            obj.geochars = json.dumps(geochars).encode()
            # macro = geochars['geoElements'].get('macrotrans', [])
            macro = []
            new_macros = item["region_new"].split(",")
            for new_macro in new_macros:
                if new_macro in regions:
                    macro.append(regions[new_macro])

            geochars['geoElements']['macrotrans'] = macro
            obj.geochars = json.dumps(geochars).encode()
            obj._p_changed = True
            obj.reindexObject()

            response.append(
                {
                    "title": obj.title,
                    "url": item["url"],
                    "macro_old": item["region_old"],
                    "macro_new": item["region_new"]
                }
            )
            logger.info("TRANS_MACRO SET for obj: %s", obj.absolute_url())

        transaction.commit()
        return response


class Retag:
    """Retag items  # 153789"""

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
            # AdaptationOptions does not have elements
            if 'metadata/adaptation-options/' in row[3]:
                continue

            item = {}
            item["uid"] = row[0]
            item["title"] = row[1]
            item["url"] = row[3]
            item["climate_service"] = row[9]
            item["just_resilience"] = row[10]
            item["mre"] = row[11]

            # import pdb; pdb.set_trace()
            if not item["climate_service"] and not item["just_resilience"] and not item["mre"]:
                continue

            obj = api.content.get(UID=item["uid"])

            if not obj:
                continue

            if not obj.elements:
                obj.elements = []
            if not hasattr(obj, "elements"):
                obj.elements = []

            if item["climate_service"] and 'CLIMATESERVICES' not in obj.elements:
                obj.elements.append('CLIMATESERVICES')
            if item["just_resilience"] and 'JUSTRESILIENCE' not in obj.elements:
                obj.elements.append('JUSTRESILIENCE')
            if item["mre"] and 'MRE' not in obj.elements:
                obj.elements.append('MRE')

            obj._p_changed = True
            obj.reindexObject()
            response.append(
                {
                    "title": obj.title,
                    "url": item["url"],
                    "keywords": obj.keywords,
                    'climate_service': 'x' if item['climate_service'] else '',
                    'just_resilience': 'x' if item['just_resilience'] else '',
                    'mre': 'x' if item['mre'] else '',
                }
            )
            logger.info("RETAG for obj: %s", obj.absolute_url())

        return response


class ObservatoryHealthImpacts:
    """Update health impacts #156631"""

    def list(self):
        # overwrite = int(self.request.form.get('overwrite', 0))

        db_item_types = [
            "eea.climateadapt.casestudy",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.aceproject",
            "eea.climateadapt.tool",
            "eea.climateadapt.video",
        ]

        catalog = api.portal.get_tool("portal_catalog")

        res = []
        i_transaction = 0
        for _type in db_item_types:
            brains = catalog.searchResults(
                portal_type=_type,
                path='/cca',
                include_in_observatory="True"
            )
            for brain in brains:
                obj = brain.getObject()
                if not hasattr(obj, "health_impacts"):
                    continue
                if not obj.health_impacts:
                    continue

                health_impacts_before = obj.health_impacts

                obj.health_impacts = []
                for health_impact in health_impacts_before:
                    if health_impact == 'Heat and cold':
                        health_impact = 'Heat'
                    elif health_impact == 'Floods and storms':
                        health_impact = 'Droughts and floods'
                    elif health_impact == 'Infectious diseases':
                        health_impact = 'Climate-sensitive diseases'
                    elif health_impact == 'Air quality and aeroallergens':
                        health_impact = 'Air pollution and aero-allergens'
                    obj.health_impacts.append(health_impact)

                i_transaction += 1
                if i_transaction % 100 == 0:
                    transaction.savepoint()

                obj._p_changed = True
                obj.reindexObject()
                logger.info("Health impacts set: %s %s",
                            brain.getURL(), obj.health_impacts)

                res.append(
                    {
                        "title": obj.title,
                        "id": brain.UID,
                        "url": brain.getURL(),
                        "health_impacts": obj.health_impacts,
                        "before": health_impacts_before,
                    }
                )

        transaction.commit()
        return res


class AdaptationNatureBasesSolutions:
    """Add nature based solutions to elements from sectors"""

    def list(self):
        # overwrite = int(self.request.form.get('overwrite', 0))

        db_item_types = [
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.aceproject",
            "eea.climateadapt.tool",
            "eea.climateadapt.video",
        ]

        catalog = api.portal.get_tool("portal_catalog")

        res = []
        i_transaction = 0
        for _type in db_item_types:
            brains = catalog.searchResults(
                portal_type=_type
            )
            for brain in brains:
                obj = brain.getObject()
                if not hasattr(obj, "sectors"):
                    continue
                if 'ECOSYSTEM' not in obj.sectors:
                    continue

                i_transaction += 1
                if i_transaction % 100 == 0:
                    transaction.savepoint()

                if not obj.elements:
                    obj.elements = []
                if not hasattr(obj, "elements"):
                    obj.elements = []
                if 'NATUREBASEDSOL' not in obj.elements:
                    obj.elements.append('NATUREBASEDSOL')
                obj.sectors.remove('ECOSYSTEM')
                obj._p_changed = True
                obj.reindexObject()
                logger.info("Migrated adaptation element: %s %s",
                            brain.getURL(), obj.elements)

                res.append(
                    {
                        "title": obj.title,
                        "id": brain.UID,
                        "url": brain.getURL(),
                        # 'publication_date': obj.publication_date,
                        "sectors": obj.sectors,
                        "elements": obj.elements,
                    }
                )

        transaction.commit()
        return res


class ElementNatureBasesSolutions:
    """Reindex NatureBasedSolution elements"""

    def list(self):
        # overwrite = int(self.request.form.get('overwrite', 0))

        catalog = api.portal.get_tool("portal_catalog")

        res = []
        i_transaction = 0
        for _type in DB_ITEM_TYPES:
            brains = catalog.searchResults(
                portal_type=_type
            )
            for brain in brains:
                obj = brain.getObject()

                if not hasattr(obj, "elements"):
                    continue
                if not obj.elements:
                    continue

                if 'NATUREBASEDSOL' not in obj.elements:
                    continue
                i_transaction += 1
                if i_transaction % 100 == 0:
                    transaction.savepoint()
                obj._p_changed = True
                obj.reindexObject()
                logger.info("Reindex: %s %s", brain.getURL(), obj.elements)

                res.append(
                    {
                        "title": obj.title,
                        "id": brain.UID,
                        "url": brain.getURL(),
                        # 'publication_date': obj.publication_date,
                        "sectors": obj.sectors,
                        "elements": obj.elements,
                    }
                )

        transaction.commit()
        return res


class ElementNatureBSReverse:
    """Ecosystem based aproach revert"""

    def list(self):
        # overwrite = int(self.request.form.get('overwrite', 0))

        db_item_types = [
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
        ]

        catalog = api.portal.get_tool("portal_catalog")

        res = []
        i_transaction = 0
        for _type in db_item_types:
            brains = catalog.searchResults(
                portal_type=_type
            )
            for brain in brains:
                obj = brain.getObject()
                if not hasattr(obj, "elements"):
                    continue
                if not obj.elements:
                    continue
                if 'NATUREBASEDSOL' not in obj.elements:
                    continue

                i_transaction += 1
                if i_transaction % 100 == 0:
                    transaction.savepoint()

                if not obj.sectors:
                    obj.sectors = []
                if not hasattr(obj, "sectors"):
                    obj.sectors = []
                if 'ECOSYSTEM' not in obj.sectors:
                    obj.sectors.append('ECOSYSTEM')
                obj.elements.remove('NATUREBASEDSOL')
                obj._p_changed = True
                obj.reindexObject()
                logger.info("Migrated adaptation element: %s %s",
                            brain.getURL(), obj.elements)

                res.append(
                    {
                        "title": obj.title,
                        "id": brain.UID,
                        "url": brain.getURL(),
                        # 'publication_date': obj.publication_date,
                        "sectors": obj.sectors,
                        "elements": obj.elements,
                    }
                )

        transaction.commit()
        return res


class RetagAO:
    """Retagging of adaptation options #261447"""

    def list(self):
        catalog = api.portal.get_tool('portal_catalog')
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

        # import pdb; pdb.set_trace()

        _elements = {
            "adaptation_mesures_and_actions": "MEASUREACTION",
            "adaptation_plans_and_strategies": "PLANSTRATEGY",
            "climate_services": "CLIMATESERVICES",
            "just_resilience": "JUSTRESILIENCE",
            "mre": "MRE",
            "nature_based_solutions": "NATUREBASEDSOL",
            "observations_ans_scenarios": "OBSERVATIONS",
            "sector_policies": "EU_POLICY",
            "vulnerability_assessment": "VULNERABILITY",
            "environmental_aspects": "ENVIRONMENTALASP",
            "mitigation_aspects": "MITIGATIONASP",
            "societal_aspects": "SOCIETALASP",
            "ecomic_aspects": "ECONOMICASP",
            "cost_benefit": "COSTBENEFIT",
            "r_u_potential": "RUPOTENTIAL",
        }

        for row in reader:
            # import pdb; pdb.set_trace()
            item = {}
            item["title"] = row[0]
            item["adaptation_mesures_and_actions"] = row[4]
            item["adaptation_plans_and_strategies"] = row[3]
            item["climate_services"] = row[6]
            item["just_resilience"] = row[8]
            item["mre"] = row[5]
            item["nature_based_solutions"] = row[9]
            item["observations_ans_scenarios"] = row[2]
            item["sector_policies"] = row[7]
            item["vulnerability_assessment"] = row[1]
            item["environmental_aspects"] = row[10]
            item["mitigation_aspects"] = row[11]
            item["societal_aspects"] = row[12]
            item["ecomic_aspects"] = row[13]
            item["cost_benefit"] = row[14]
            item["r_u_potential"] = row[15]

            obj = None
            brains = catalog.searchResults(
                {'portal_type': ['eea.climateadapt.casestudy', 'eea.climateadapt.adaptationoption'], 'path': '/cca/en'})
            for brain in brains:
                if brain.getObject().title == item['title']:
                    obj = brain.getObject()

            if not obj:
                continue
            # import pdb; pdb.set_trace()
            abc = []
            [abc.append(x) for x in item if item[x]]
            data = [_elements[x] for x in abc if x in _elements]

            obj.elements = data
            obj._p_changed = True
            notify(ObjectModifiedEvent(obj))
            obj.reindexObject()

            response.append(
                {
                    "title": obj.title,
                    "url": obj.absolute_url(),
                }
            )
            logger.info("Retag elements for obj: %s",
                        obj.absolute_url())

            languages = ['de', 'es', 'fr', 'it', 'pl']
            for language in languages:
                languagePath = obj.absolute_url_path().replace("/en/", "/"+language+"/")
                languageBrains = catalog.searchResults(
                    {'portal_type': ['eea.climateadapt.casestudy', 'eea.climateadapt.adaptationoption'], 'path': "/cca"+languagePath})
                for languageBrain in languageBrains:
                    languageObj = languageBrain.getObject()
                    if languageObj.absolute_url_path() == languagePath:
                        languageObj.elements = data
                        languageObj._p_changed = True
                        logger.info("Retag elements for obj language: %s",
                                    languageObj.absolute_url())

        return response


class RetagCS:
    """Retagging of case studies #261447"""

    def list(self):
        catalog = api.portal.get_tool('portal_catalog')
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
        _elements = {
            "adaptation_mesures_and_actions": "MEASUREACTION",
            "adaptation_plans_and_strategies": "PLANSTRATEGY",
            "climate_services": "CLIMATESERVICES",
            "just_resilience": "JUSTRESILIENCE",
            "mre": "MRE",
            "nature_based_solutions": "NATUREBASEDSOL",
            "observations_ans_scenarios": "OBSERVATIONS",
            "sector_policies": "EU_POLICY",
            "vulnerability_assessment": "VULNERABILITY",
        }

        for row in reader:
            item = {}
            item["title"] = row[0]

            item["just_resilience"] = None
            item["nature_based_solutions"] = None

            item["vulnerability_assessment"] = row[1]
            item["observations_ans_scenarios"] = row[2]
            item["adaptation_plans_and_strategies"] = row[3]
            item["adaptation_mesures_and_actions"] = row[4]
            item["climate_services"] = row[5]
            item["sector_policies"] = row[6]
            item["mre"] = row[7]

            obj = None
            brains = catalog.searchResults(
                {'portal_type': 'eea.climateadapt.casestudy', 'path': '/cca/en'})
            for brain in brains:
                if brain.getObject().title == item['title']:
                    obj = brain.getObject()

            if not obj:
                continue
            # import pdb; pdb.set_trace()
            abc = []
            [abc.append(x) for x in item if item[x]]
            data = [_elements[x] for x in abc if x in _elements]

            obj.elements = data
            obj._p_changed = True
            response.append(
                {
                    "title": obj.title,
                    "url": obj.absolute_url(),
                }
            )
            logger.info("Retag elements for obj: %s",
                        obj.absolute_url())
            logger.info(data)

        return response


class UndoSector:
    """Add the new sectors #257706"""

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        reset_sectors = ['BUSINESSINDUSTRY', 'ICT', 'CULTURALHERITAGE',
                         'LANDUSE', 'TOURISMSECTOR', 'MOUNTAINAREAS']

        brains = catalog.searchResults({
            'path': '/cca/en/metadata',
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
        })

        i_count = 0
        for brain in brains:
            i_count = i_count+1
            obj = brain.getObject()
            if hasattr(obj, 'sectors') and isinstance(obj.sectors, list):
                for reset_sector in reset_sectors:
                    if reset_sector in obj.sectors:
                        obj.sectors.remove(reset_sector)

                logger.info("%s from %s %s", i_count,
                            len(brains), obj.absolute_url())

                obj._p_changed = True
                obj.reindexObject()
        logger.info("DONE")

        return 'done'


class NewSector:
    """Add the new sectors #257706"""

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

        for row in reader:
            item = {}
            item["uid"] = row[0]
            item["title"] = row[1]
            item["sector"] = row[2]

            if not len(item['sector']):
                continue
            # import pdb; pdb.set_trace()
            obj = api.content.get(UID=item["uid"])

            if not obj:
                logger.info("Not found: %s %s", item['uid'], item['title'])
                continue

            if isinstance(obj.sectors, tuple):
                obj.sectors = list(obj.sectors)
            try:
                obj.sectors.append(item['sector'])
                obj._p_changed = True
                obj.reindexObject()
            except Exception as err:
                import pdb
                pdb.set_trace()

            response.append(
                {
                    "title": obj.title,
                    "url": obj.absolute_url(),
                }
            )
            logger.info("%s %s", item['uid'], type(obj.sectors))

        return response


class SyncAttributes:
    """Add the new sectors #257706"""

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        attribute_names = ['sectors', 'elements']
        i_transaction = 0

        brains = catalog.searchResults({
            'path': '/cca/en/metadata'
        })
        for brain in brains:
            obj = brain.getObject()

            try:
                translations = TranslationManager(obj).get_translations()
            except Exception:
                logger.info("Problem getting translations for: %s",
                            obj.absolute_url())
                translations = []
            for language in translations:
                obj_lang = translations[language]
                for attribute_name in attribute_names:
                    if hasattr(obj, attribute_name):
                        value = getattr(obj, attribute_name)
                        setattr(obj_lang, attribute_name, value)
                obj_lang._p_changed = True
                obj_lang.reindexObject()
                i_transaction += 1
                if i_transaction % 100 == 0:
                    transaction.savepoint()
            logger.info("%s", obj.absolute_url())

        transaction.commit()

        return 'done'
