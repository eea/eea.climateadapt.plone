# -*- coding: utf-8 -*-
import csv
import json
import logging
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
                logger.info("Migrated site origin : %s %s", brain.getURL(), obj.origin_website)

            elif origin_website and isinstance(origin_website, str):
                obj.origin_website = [origin_website]
                logger.info("Migrated site origin : %s %s", brain.getURL(), obj.origin_website)

            elif origin_website is None:
                obj.origin_website = []
                logger.info("Migrated site origin : %s %s", brain.getURL(), obj.origin_website)

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
                    logger.info("Migrated health impact for obj: %s %s", brain.getURL(), obj.health_impacts)

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
            logger.info("Migrated funding programme for obj: %s", obj.absolute_url())

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


class MigrateTransnationalRegionsDatabaseItems(BrowserView):
    """ Update transnational regions

    --- The request simplified ------------------------------------------------
    ** If we replace with a single tag, the first replace will be lost. So,
    instead of REPLACE we will ADD the new tag then the old Balkan-M will be
    deleted for all. This way Balkan-M + Greece => Mediterranean AND also
    Balkan-M + Greece => Adriatic-I Region.

    IF content_types
    AND Balkan-Mediterranean
        IF Greece
        OR Albania
        OR Macedonia
        OR Bulgaria
            => REPLACE Balkan-Mediterranean WITH Mediterranean               **

        IF Greece
        OR Albania
        OR Macedonia
            => REPLACE Balkan-Mediterranean WITH Adriatic-Ionian Region      **

        IF Bulgaria
            => REPLACE Balkan-Mediterranean WITH Danube Region               **

        IF countries not mentioned
            => DELETE tag Balkan-Mediterranean

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
            => ADD tag MEDITERRANEAN SEA BASIN

    AND Danube Area
        IF Black Sea
            => ADD tag Black Sea Basin

    AND South East Europe
        IF Morocco
        OR Africa
        OR Canary
            => ADD tag Mid-Atlantic

    --- The request -----------------------------------------------------------
    ALL database items EXCEPT: case studies, indicators, adaptation options
    a. For the items that are currently tagged for Balkan Mediterranean region:
        REPLACE THE  TAG "Balkan-Mediterranean" WITH
        i. MEDITERRANEAN tag (items with the following countries selected
        or mentioned in the text:
        Greece OR Albania OR Macedonia OR Bulgaria)
        ii. ADRIATIC-IONIAN REGION  tag (items with the following
        countries selected or mentioned in the text:
        Greece OR Albania OR Macedonia)
        iii. DANUBE REGION tag (items with Bulgaria selected or mentioned)
        iv. NOTHING (DELETE tag) if countries are not mentioned

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
    """ Database INDICATORS (that are always tagged for all regions)
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
       https://taskman.eionet.europa.eu/issues/156654#note-2
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
                {'url': 'copernicus-climate-change-service-ecmw', 'id': 0, 'object': None},
            'European Centre for Disease Prevention and Control - Climate-ADAPT (europa.eu)':
                {'url': 'european-centre-for-disease-prevention-and-control-ecdc', 'id': 0, 'object': None},
            'European Commission - Climate-ADAPT (europa.eu)':
                {'url': 'european-commission', 'id': 0, 'object': None},
            'European Environment Agency - Climate-ADAPT (europa.eu)':
                {'url': 'european-environment-agency-eea', 'id': 0, 'object': None},
            'European Food Safety Authority - Climate-ADAPT (europa.eu)':
                {'url': 'european-food-safety-authority', 'id': 0, 'object': None},
            'Lancet Countdown - Climate-ADAPT (europa.eu)':
                {'url': 'lancet-countdown', 'id': 0, 'object': None},
            'World Health Organization - Regional Office for Europe - Climate-ADAPT (europa.eu)':
                {'url': 'who-regional-office-for-europe-who-europe', 'id': 0, 'object': None},
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
                map_organisations[title]['id'] = util.getId(orgs[0].getObject())
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
                logger.warning("Partner not found: %s [%s]", item['url'], item['partners'])
                continue

            partner_object_id = map_organisations[item['partners']]['id']
            if not partner_object_id:
                logger.warning("Partner not match: %s [%s]", item['url'], item['partners'])
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

                    logger.info("Migrated contributors for obj: %s", brain.getURL())

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

                    response.append({"title": obj.title, "url": brain.getURL()})
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
                    logger.info("Migrated source type for obj: %s", brain.getURL())


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

                if hasattr(obj,"health_impacts") \
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
                {'url': 'copernicus-climate-change-service-ecmw', 'id': 0, 'object': None},
            'European Centre for Disease Prevention and Control - Climate-ADAPT (europa.eu)':
                {'url': 'european-centre-for-disease-prevention-and-control-ecdc', 'id': 0, 'object': None},
            'European Commission - Climate-ADAPT (europa.eu)':
                {'url': 'european-commission', 'id': 0, 'object': None},
            'European Environment Agency - Climate-ADAPT (europa.eu)':
                {'url': 'european-environment-agency-eea', 'id': 0, 'object': None},
            'European Food Safety Authority - Climate-ADAPT (europa.eu)':
                {'url': 'european-food-safety-authority', 'id': 0, 'object': None},
            'Lancet Countdown - Climate-ADAPT (europa.eu)':
                {'url': 'lancet-countdown', 'id': 0, 'object': None},
            'World Health Organization - Regional Office for Europe - Climate-ADAPT (europa.eu)':
                {'url': 'who-regional-office-for-europe-who-europe', 'id': 0, 'object': None},
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
                map_organisations[title]['id'] = util.getId(orgs[0].getObject())
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
                logger.warning("Partner not found: %s [%s]", item['url'], item['partners'])
                continue

            partner_object_id = map_organisations[item['partners']]['id']
            if not partner_object_id:
                logger.warning("Partner not match: %s [%s]", item['url'], item['partners'])
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
        brains = catalog.searchResults(portal_type="eea.climateadapt.aceproject")

        res = []
        for brain in brains:
            obj = brain.getObject()

            if hasattr(obj,"funding_programme") \
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

                obj.health_impacts = [health_impacts.get(item["health_impact"], None)]
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


#142756
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
            #item["uid"] = row[6]

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
            #macro = geochars['geoElements'].get('macrotrans', [])
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
                path='/cca/en',
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
                logger.info("Health impacts set: %s %s", brain.getURL(), obj.health_impacts)

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
                    obj.elements.append('NATUREBASEDSOL');
                obj.sectors.remove('ECOSYSTEM')
                obj._p_changed = True
                obj.reindexObject()
                logger.info("Migrated adaptation element: %s %s", brain.getURL(), obj.elements)

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
                    obj.sectors.append('ECOSYSTEM');
                obj.elements.remove('NATUREBASEDSOL')
                obj._p_changed = True
                obj.reindexObject()
                logger.info("Migrated adaptation element: %s %s", brain.getURL(), obj.elements)

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
