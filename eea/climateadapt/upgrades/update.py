from zope.interface import alsoProvides
from eea.climateadapt.interfaces import (
    IMainTransnationalRegionMarker,
    ITransnationalRegionMarker,
)
import transaction
import json
import logging

from Acquisition import aq_self
from plone.api import portal
from plone.app.textfield.interfaces import ITransformer
from Products.MimetypesRegistry.mime_types.magic import guessMime
from eea.rdfmarshaller.actions.pingcr import ping_CRSDS

from plone import api

logger = logging.getLogger("eea.climateadapt.migration")
default_profile = "profile-eea.climateadapt:default"


def fixtiles(context):
    """Noop migrator, as it's already recorded in GS registry"""
    pass


def update_to_8(context):
    return
    if context.readDataFile("eea.climateadapt.update.txt") is None:
        return

    site = context.getSite()

    _fix_covers(site)
    _fix_content(site)


def update_to_9(context):
    return
    if context.readDataFile("eea.climateadapt.update_9.txt") is None:
        return

    _fix_content(context.getSite())


def _fix_content(site):
    """Fix the tags in all objects in the site"""
    # TODO: rename this function, needs better name

    catalog = site.portal_catalog

    searchTypes = [
        "eea.climateadapt.aceproject",
        "eea.climateadapt.adaptationoption",
        "eea.climateadapt.casestudy",
        "eea.climateadapt.guidancedocument",
        "eea.climateadapt.indicator",
        "eea.climateadapt.informationportal",
        "eea.climateadapt.mapgraphdataset",
        "eea.climateadapt.organisation",
        "eea.climateadapt.publicationreport",
        "eea.climateadapt.researchproject",
        "eea.climateadapt.tool",
    ]
    results = catalog.searchResults({"portal_type": searchTypes})

    for brain in results:
        obj = aq_self(brain.getObject())

        if not (hasattr(obj, "special_tags") or hasattr(obj, "specialtagging")):
            continue

        tags = []

        for attr in ["special_tags", "specialtagging"]:
            st = getattr(obj, attr, []) or []

            if isinstance(st, basestring):
                tags.append(st)
            else:
                tags.extend(st)

        tags = _fix_tags(tags)

        if tags:
            logger.info("Fixing tags on %s", brain.getURL())
            obj.special_tags = tags
            obj.reindexObject()


def _fix_covers(self):
    """Fix tags in all cover tiles"""
    # TODO: rename this function, needs better name

    covers = self.portal_catalog.searchResults(
        portal_type="collective.cover.content")

    for cover in covers:
        cover = cover.getObject()

        if hasattr(cover, "__annotations__"):
            for tile_id in list(cover.__annotations__.keys()):
                tile_id = tile_id.encode()

                if "plone.tiles.data" in tile_id:
                    tile = cover.__annotations__[tile_id]

                    if "special_tags" and "search_text" in tile.keys():
                        tile["special_tags"] = _fix_tags(tile["special_tags"])
                        tile["search_text"] = _fix_tags(tile["search_text"])
                        tile._p_changed = True
                        cover.reindexObject()


def _fix_tags(tags):
    # TODO: rename this function, needs better name

    if isinstance(tags, (list, tuple)):
        tags = [i.replace("-", "_") for i in tags]
    elif tags:
        tags = tags.replace("-", "_")

    return list(set(filter(None, tags)))


def update_to_22(context):
    return
    site = context.getSite()
    catalog = site.portal_catalog

    # Bring back the featured field values from the old database
    ids = (
        "3402 3403 4704 4706 4202 3323 3505 4102 5301 5901 6301 3503 3504 "
        "3326 3325 4302 4703 3502 4201 3401 3801 4705 3327 4301 6001 4901 "
        "5001 5002 5003 5101 5201 4401 3311 5801 5503 5401 5501 5601 5902 "
        "6201 6101 6202"
    )
    ids = [int(x) for x in ids.split(" ") if x]

    for id in ids:
        res = catalog.searchResults(acemeasure_id=id)

        if res:
            obj = res[0].getObject()
            obj.featured = True
            obj._p_changed = True
            logger.info("Fixed featured for %s", res[0].getURL())
        else:
            logger.warn("Couldn't get measure with id %s", id)

    # fix sectors, split Agriculture and Infrastructure sectors
    results = catalog.searchResults(sectors="AGRICULTURE")

    for b in results:
        b = b.getObject()

        if hasattr(b, "sectors"):
            if b.sectors is None:
                continue
            else:
                if "AGRICULTURE" in b.sectors:
                    b.sectors = sorted(set(b.sectors + ["FORESTRY"]))
                    b._p_changed = True
                    b.reindexObject()

    results = catalog.searchResults(sectors="INFRASTRUCTURE")

    for b in results:
        b = b.getObject()

        if hasattr(b, "sectors"):
            if b.sectors is None:
                continue
            else:
                if "INFRASTRUCTURE" in b.sectors:
                    b.sectors.remove("INFRASTRUCTURE")
                    b.sectors = sorted(
                        set(b.sectors + ["ENERGY", "TRANSPORT", "BUILDINGS"])
                    )
                    b.reindexObject()
                    b._p_changed = True

    # assign a measure id for all case studies, it's needed for the /sat map
    _ids = sorted(filter(None, catalog.uniqueValuesFor("acemeasure_id")))
    results = catalog.searchResults(portal_type="eea.climateadapt.casestudy")

    for b in results:
        obj = b.getObject()
        mid = getattr(obj, "_acemeasure_id", None)

        if mid:
            continue
        mid = _ids[-1] + 1
        obj._acemeasure_id = mid
        obj.reindexObject(idxs=["acemeasure_id"])
        _ids.append(mid)


def update_to_23(context):
    return
    site = context.getSite()
    catalog = site.portal_catalog

    MAPPING = {
        "INFRASTRUCTURE": ["ENERGY", "TRANSPORT", "BUILDINGS"],
        "AGRICULTURE": ["FORESTRY", "AGRICULTURE"],
        "AGRI_AND_FOREST": ["FORESTRY", "AGRICULTURE"],
    }

    profiles = catalog.searchResults(
        portal_type="eea.climateadapt.city_profile")

    for b in profiles:
        obj = b.getObject()

        if hasattr(obj, "key_vulnerable_adaptation_sector"):
            if obj.key_vulnerable_adaptation_sector is None:
                continue

            sectors = obj.key_vulnerable_adaptation_sector

            if isinstance(sectors, str):
                sectors = set(
                    sectors,
                )
            else:
                sectors = set(sectors)

            for val in MAPPING.keys():
                if val in sectors:
                    sectors.remove(val)
                    sectors.update(MAPPING.get(val))
                    obj._p_changed = True

            if obj._p_changed is True:
                logger.info("Fixed sectors on %s", obj.absolute_url())
                obj.key_vulnerable_adaptation_sector = sectors
                obj.reindexObject()


def update_to_24(context):
    return
    site = context.getSite()
    catalog = site.portal_catalog
    query = {
        "portal_type": [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.mapgraphdataset",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.researchproject",
            "eea.climateadapt.tool",
        ]
    }

    results = catalog.searchResults(**query)

    for b in results:
        obj = b.getObject()

        if obj.climate_impacts is None:
            logger.info("Fixing tags on %s", b.getURL())
            obj.climate_impacts = []
            obj._p_changed = True
            obj.reindexObject()


def update_to_25(context):
    return ""
    site = context.getSite()
    catalog = site.portal_catalog
    query = {
        "portal_type": [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.mapgraphdataset",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.researchproject",
            "eea.climateadapt.tool",
        ]
    }
    results = catalog.searchResults(**query)

    extension = {
        "application/pdf": ".pdf",
        "application/zip": ".zip",
        "image/jpeg": ".jpg",
    }

    for b in results:
        items = b.getObject().contentValues()

        for item in items:
            if item.portal_type == "File":
                filex = item.file
                filetype = guessMime(filex._data)

                if filetype is not None:
                    if filex.filename.find(extension[filetype]) == -1:
                        filex.contentType = filetype
                        filex.filename = filex.filename.replace(
                            ".", extension[filetype]
                        )
                        filex._p_changed = True
                        logger.info("Fixing file: %s", filex.filename)
                        logger.info("URL: %s", item.absolute_url())
                else:
                    logger.info("Not Fixed:")
                    logger.info("Type: %s", filetype)
                    logger.info("URL: %s", item.absolute_url())
                    logger.info("Item: %s", item)


def update_to_26(context):
    return
    site = context.getSite()
    catalog = site.portal_catalog
    query = {
        "portal_type": [
            "eea.climateadapt.casestudy",
        ]
    }
    results = catalog.searchResults(**query)

    for b in results:
        obj = b.getObject()

        if obj.geochars:
            if obj.geochars.find("PANONIAN") != -1:
                obj.geochars = obj.geochars.replace("PANONIAN", "PANNONIAN")
                logger.info("Fixing Bioregion on %s", obj.absolute_url())
                logger.info("New geochars: %s", obj.geochars)
    logger.info("Finished the update.")


def update_to_27(context):
    """Dummy upgrade"""

    return


def update_to_28(context):
    return
    site = context.getSite()
    catalog = site.portal_catalog
    query = {
        "portal_type": [
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.organisation",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.tool",
            "eea.climateadapt.indicator",
            "eea.climateadapt.mapgraphdataset",
            "eea.climateadapt.researchproject",
        ]
    }
    results = catalog.searchResults(**query)

    for b in results:
        obj = b.getObject()
        changed = False

        if obj.sectors in [None, []]:
            logger.info("Fixing sector on %s", obj.absolute_url())
            obj.sectors = ()
            changed = True

        if obj.climate_impacts in [None, []]:
            logger.info("Fixing climate impacts on %s", obj.absolute_url())
            obj.climate_impacts = ()
            changed = True

        if changed:
            logger.info("Reindexing.")
            obj.reindexObject()
            obj._p_changed = True


def update_to_29(context):
    return
    site = context.getSite()
    catalog = site.portal_catalog
    query = {
        "portal_type": [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.mapgraphdataset",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.researchproject",
            "eea.climateadapt.tool",
        ]
    }
    results = catalog.searchResults(**query)

    for b in results:
        obj = b.getObject()

        if obj.websites in [None, []]:
            logger.info("Websites value: %s", obj.websites)
            logger.info("Fixing websites on url: %s", obj.absolute_url())
            obj.websites = ()
            obj._p_changed = True
            obj.reindexObject()


def update_to_30(context):
    return
    site = context.getSite()
    catalog = site.portal_catalog
    query = {
        "portal_type": [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.mapgraphdataset",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.researchproject",
            "eea.climateadapt.tool",
        ]
    }
    results = catalog.searchResults(**query)

    for b in results:
        obj = b.getObject()
        changed = False

        if obj.sectors in [None, []]:
            logger.info("Fixing sector on %s", obj.absolute_url())
            obj.sectors = ()
            changed = True

        if obj.climate_impacts in [None, []]:
            logger.info("Fixing climate impacts on %s", obj.absolute_url())
            obj.climate_impacts = ()
            changed = True

        if hasattr(obj, "relevance"):
            if obj.relevance is None:
                logger.info("Fixing relevance on %s", obj.absolute_url())
                obj.relevance = []
                changed = True

        if changed:
            logger.info("Reindexing.")
            obj.reindexObject()
            obj._p_changed = True


def update_to_33(context):
    """Fix the value of the source field since we changed the field from
    richtext to textline
    """

    return
    catalog = portal.get_tool(name="portal_catalog")
    query = {
        "portal_type": [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.mapgraphdataset",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.researchproject",
            "eea.climateadapt.tool",
        ]
    }
    results = catalog.searchResults(**query)

    for brain in results:
        try:
            obj = brain.getObject()
        except:
            logger.warn("SKIPPED %s", brain.getURL())

            continue

        if hasattr(obj, "source"):
            if obj.source:
                bumblebee = ITransformer(obj)
                obj.source = bumblebee(obj.source, "text/plain")
                logger.info("Migrated source field for %s", obj.absolute_url())
                obj._p_changed = True
                obj.reindexObject()


def update_to_34(context):
    return
    logger.info("Upgrading to 34")

    # need to reimport eea.climateadapt, it has updated registry settings
    context.runImportStepFromProfile(default_profile, "plone.app.registry")


def update_to_35(context):
    """Migrate layer id from website to gis_layer_id field"""

    return
    catalog = portal.get_tool(name="portal_catalog")
    query = {
        "portal_type": [
            "eea.climateadapt.mapgraphdataset",
        ]
    }
    results = catalog.searchResults(**query)

    for brain in results:
        obj = brain.getObject()
        websites = obj.websites

        if isinstance(websites, (list, tuple)):
            for layer_id in websites:
                if check_layer_id(layer_id):
                    obj.gis_layer_id = layer_id
                    obj.websites = [i for i in websites if i != layer_id]
                    obj.reindexObject()
                    obj._p_changed = True
                    logger.info("Migrated layer for %s", obj.absolute_url())
        elif isinstance(websites, str):
            if check_layer_id(layer_id):
                obj.gis_layer_id = websites
                obj.websites = ""
                obj.reindexObject()
                obj._p_changed = True
                logger.info("Migrated layer for %s", obj.absolute_url())
    logger.info("Finished the layer ids migration %s", obj.absolute_url())


def check_layer_id(value):
    if not value:
        return False

    if value.startswith("/") or value.startswith("http"):
        return False

    return True


def update_to_36(context):
    return
    logger.info("Upgrading to 36")

    # need to reimport eea.climateadapt, it has updated registry settings
    context.runImportStepFromProfile(default_profile, "typeinfo")
    context.runImportStepFromProfile(default_profile, "propertiestool")
    context.runImportStepFromProfile(default_profile, "repositorytool")
    context.runImportStepFromProfile(default_profile, "workflow")
    context.runImportStepFromProfile(default_profile, "contentrules")


def update_to_37(context):
    return
    logger.info("Upgrading to 37")
    logger.info("Setting the proper effective date for some aceprojects")

    catalog = portal.get_tool(name="portal_catalog")
    query = {"portal_type": "eea.climateadapt.aceproject",
             "review_state": "published"}
    brains = catalog.searchResults(**query)

    for brain in brains:
        obj = brain.getObject()

        if obj.effective_date is None:
            wf_history = obj.workflow_history.get("cca_items_workflow", [])

            for wf in wf_history:
                if wf.get("action", "") == "publish":
                    obj.effective_date = wf.get("time", None)
                    obj.reindexObject()
                    obj._p_changed = True

                    continue
    logger.info("Finished modifying the effective dates for aceprojects")


def update_to_39(context):
    return
    logger.info("Upgrading to 39")
    logger.info("Setting the new macrotransnational regions for some aceitems")

    catalog = portal.get_tool(name="portal_catalog")
    query = {
        "portal_type": [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.mapgraphdataset",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.researchproject",
            "eea.climateadapt.tool",
        ]
    }

    brains = catalog.searchResults(**query)
    logger.info("Got %s results." % len(brains))
    items_count = 0

    for b in brains:
        obj = b.getObject()

        items_count += 1

        if items_count % 100 == 0:
            logger.info("Went through %s brains" % items_count)

        if obj.geochars in [None, "", "", []]:
            continue

        geochars = json.loads(obj.geochars)
        macro = geochars["geoElements"].get("macrotrans", [])
        modified = False

        if macro:
            if "TRANS_MACRO_CAR_AREA" in macro:
                macro.append("TRANS_MACRO_AMAZONIA")
                modified = True

            if "TRANS_MACRO_SE_EUR" in macro:
                macro.remove("TRANS_MACRO_SE_EUR")
                macro.append("TRANS_MACRO_DANUBE")
                macro.append("TRANS_MACRO_ADR_IONIAN")
                macro.append("TRANS_MACRO_BALKAN_MED")
                modified = True

            if "TRANS_MACRO_MACRONESIA" in macro:
                macro.remove("TRANS_MACRO_MACRONESIA")

                if "TRANS_MACRO_ATL_AREA" not in macro:
                    macro.append("TRANS_MACRO_ATL_AREA")
                modified = True

            if modified:
                logger.info("Reindexing object %s" % obj.absolute_url())
                geochars["geoElements"]["macrotrans"] = macro
                obj.geochars = json.dumps(geochars).encode()
                obj._p_changed = True
                obj.reindexObject()
    logger.info("Finished upgrade 39")


def update_to_41(context):
    return
    logger.info("Upgrading to 41")
    logger.info("Setting the search type to CONTENT for News/Events/Links")

    catalog = portal.get_tool(name="portal_catalog")
    query = {"portal_type": ["News Item", "Event", "Link"]}

    brains = catalog.searchResults(**query)
    logger.info("Got %s results." % len(brains))
    items_count = 0

    for b in brains:
        obj = b.getObject()

        items_count += 1

        if items_count % 100 == 0:
            logger.info("Went through %s brains" % items_count)

        if not hasattr(obj, "search_type"):
            setattr(obj, "search_type", "CONTENT")
            obj._p_changed = True
            obj.reindexObject()
            logger.info("Reindexing object %s" % obj.absolute_url())


def update_to_42(context):
    return
    logger.info("Upgrading to 42")
    logger.info("Updating the invalidating cache permission with new roles")

    context.runImportStepFromProfile(default_profile, "rolemap")

    logger.info("Finished upgrade 42")


def update_to_43(context):
    return
    logger.info("Upgrading to 43")
    logger.info("Importing workflow")

    context.runImportStepFromProfile(
        "profile-eea.climateadapt:eeaclimateadapt_to_43", "workflow"
    )

    logger.info("Finished upgrade 43")


def update_to_47(context):
    return
    logger.info("Upgrading to 47.")

    catalog = portal.get_tool(name="portal_catalog")
    query = {
        "portal_type": [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.mapgraphdataset",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.researchproject",
            "eea.climateadapt.tool",
            # 'eea.climateadapt.city_profile',
        ]
    }
    results = catalog.searchResults(**query)
    logger.info("Got %s results." % len(results))
    items_count = 0

    for brain in results:
        obj = brain.getObject()

        if items_count % 100 == 0:
            logger.info("Went through %s brains" % items_count)
        items_count += 1
        modified = 0
        climate = obj.climate_impacts
        sectors = obj.sectors

        if len(climate) == 7 and "NONSPECIFIC" not in climate:
            modified += 1
            climate = ["NONSPECIFIC"]
        if len(sectors) == 13 and "NONSPECIFIC" not in sectors:
            modified += 1
            sectors = ["NONSPECIFIC"]

        if modified != 0:
            obj.climate_impacts = climate
            obj.sectors = sectors
            obj.reindexObject()
            obj._p_changed = True
    logger.info("Finished upgrade 47.")


def update_to_57(context):
    return
    logger.info("Upgrading to 57.")

    catalog = portal.get_tool(name="portal_catalog")
    query = {
        "portal_type": [
            "eea.climateadapt.aceproject",
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
            "eea.climateadapt.guidancedocument",
            "eea.climateadapt.indicator",
            "eea.climateadapt.informationportal",
            "eea.climateadapt.mapgraphdataset",
            "eea.climateadapt.organisation",
            "eea.climateadapt.publicationreport",
            "eea.climateadapt.researchproject",
            "eea.climateadapt.tool",
            # 'eea.climateadapt.city_profile',
        ]
    }
    results = catalog.searchResults(**query)
    logger.info("Got %s results." % len(results))
    items_count = 0

    options = {}
    options["create"] = False
    options["service_to_ping"] = "http://semantic.eea.europa.eu/ping"
    for brain in results:
        obj = brain.getObject()

        if items_count % 100 == 0:
            logger.info("Went through %s brains" % items_count)
        items_count += 1

        if hasattr(obj, "geochars"):
            if obj.geochars:
                if obj.geochars.find("FYROM") != -1:
                    logger.info("Fixing geochars on %s", obj.absolute_url())
                    obj.geochars = obj.geochars.replace("FYROM", "MK")
                    logger.info("New geochars: %s", obj.geochars)
                    obj.reindexObject()
                    obj._p_changed = True

                    url = brain.getURL()
                    options["obj_url"] = url + "/@@rdf"
                    logger.info("Pinging: %s", url)
                    ping_CRSDS(context, options)
                    logger.info("Finished pinging: %s", url)
    logger.info("Finished upgrade 57.")


def update_to_65(setup_tool=None):
    """Run upgrade"""
    logger.info("Running upgrade (Python): New indexes and catalog fields")
    setup = api.portal.get_tool("portal_setup")
    setup.runImportStepFromProfile("eea.climateadapt:default", "catalog")
    logger.info("Done")


def update_to_66(context):
    logger.info("Upgrading to 66.")

    catalog = portal.get_tool(name="portal_catalog")
    query = {
        "portal_type": [
            "eea.climateadapt.adaptationoption",
            "eea.climateadapt.casestudy",
        ]
    }
    results = catalog.searchResults(**query)
    logger.info("Got %s results." % len(results))
    items_count = 0

    for brain in results:
        obj = brain.getObject()

        if items_count % 100 == 0:
            logger.info("Went through %s brains" % items_count)
        items_count += 1
        modified = False

        sectors = obj.sectors
        elements = obj.elements
        if elements is None:
            elements = []

        if sectors is not None and "ECOSYSTEM" in sectors:
            updated_elements = elements
            if updated_elements is None:
                updated_elements = []
            if "NATUREBASEDSOL" not in elements:
                updated_elements.append("NATUREBASEDSOL")

            updated_sectors = sectors
            updated_sectors.remove("ECOSYSTEM")
            modified = True

        if modified is True:
            logger.info("Updating %s" % obj.absolute_url())
            logger.info("NEW SECTORS %s" % ", ".join(updated_sectors))
            logger.info("NEW ELEM %s" % ", ".join(updated_elements))
            obj.sectors = updated_sectors
            obj.elements = updated_elements
            obj.reindexObject()
            obj._p_changed = True
    logger.info("Finished upgrade 66.")


def reindex_health_impacts(context):
    catalog = portal.get_tool(name="portal_catalog")
    keys = catalog.uniqueValuesFor("health_impacts")
    brains = catalog.searchResults(health_impacts=keys)

    i = 0
    for brain in brains:
        obj = brain.getObject()
        obj.reindexObject()
        i += 1
        if i % 1000 == 0:
            transaction.savepoint()

    logger.info("Finished reindexing health_impacts.")


def update_transnational_regions(context):
    catalog = portal.get_tool(name="portal_catalog")
    keys = [
        "alpine-space",
        "atlantic-area",
        "baltic-sea-region",
        "central-europe",
        "danube",
        "mediterranean",
        "north-sea",
        "north-west-europe",
        "northern-periphery",
        "south-west-europe",
        "adriatic-ionian",
    ]
    brains = catalog.searchResults(id=keys)

    for brain in brains:
        obj = brain.getObject()
        if ITransnationalRegionMarker.providedBy(obj):
            alsoProvides(obj, IMainTransnationalRegionMarker)
        obj.reindexObject()
        logger.info("Remarked transnational region: %s", obj.absolute_url())


def update_budget_ranges(context):
    catalog = portal.get_tool(name="portal_catalog")
    from eea.climateadapt.vocabulary import budget_ranges_reverse_map

    brains = catalog.searchResults(portal_type="mission_funding_cca")
    for brain in brains:
        obj = brain.getObject()
        ranges = getattr(obj, "budget_range", None)
        if ranges:
            obj.budget_range = [budget_ranges_reverse_map[x]
                                for x in obj.budget_range]
            obj._p_changed = True
            logger.info(
                "Migrated budget_range for %s, %r", obj.absolute_url(), obj.budget_range
            )

    logger.info("Done migrating budget_range")


admin_users = (
    "ghitab",
    "tibiadmin",
    "tibi",
    "tiberich",
    "eugentripon",
    "iulianpetchesi",
    "krisztina",
)


def get_new_creator(creators, wf_creator):
    if wf_creator not in admin_users:
        return [wf_creator]

    filtered_creators = [x for x in creators if x not in admin_users]

    if filtered_creators:
        return [filtered_creators[0]]

    return [wf_creator]


def fix_creators(context):
    catalog = portal.get_tool(name="portal_catalog")
    brains = catalog.searchResults(
        missing_index=True,
        path="/cca/en",
        # path="/cca/en/countries-regions/transnational-regions/alpine-space",
    )  # this returns all objects
    # import pdb
    #
    # pdb.set_trace()

    for brain in brains:
        try:
            raw_obj = brain.getObject()
            url = raw_obj.absolute_url()
            obj = raw_obj.aq_inner.aq_self
            creators = obj.creators
        except Exception:
            continue

        if len(creators) == 1 and creators[0] not in admin_users:
            continue

        try:
            wfh = obj.workflow_history
        except Exception:
            # logger.info("No workflow: %s", url)
            continue

        wf_creator = None

        workflow = wfh.get("cca_webpages_workflow", {}) or wfh.get(
            "cca_items_workflow", {}
        )

        wf_data = [
            (x["actor"], x["time"]) for x in workflow if x["action"] is None
        ] or [(x["actor"], x["time"]) for x in workflow]

        if wf_data:
            wf_creator = wf_data[0][0]

        if not wf_creator:
            continue

        creators = get_new_creator(creators, wf_creator)
        if creators != obj.creators:
            logger.info(
                "Fixing creator for %s, %s => %s",
                url,
                obj.creators,
                creators,
            )
            obj.creators = creators
            obj._p_changed = True
            obj.reindexObject(idxs=["Creator"])

    logger.info("Done fixing creators")
