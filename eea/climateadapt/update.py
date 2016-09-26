from Acquisition import aq_self
import logging

logger = logging.getLogger('eea.climateadapt.migration')


def fixtiles(context):
    """ Noop migrator, as it's already recorded in GS registry
    """
    pass


def update_to_8(context):
    if context.readDataFile('eea.climateadapt.update.txt') is None:
        return

    site = context.getSite()

    _fix_covers(site)
    _fix_content(site)


def update_to_9(context):
    if context.readDataFile('eea.climateadapt.update_9.txt') is None:
        return

    _fix_content(context.getSite())


def _fix_content(site):
    """ Fix the tags in all objects in the site
    """
    # TODO: rename this function, needs better name

    catalog = site.portal_catalog

    searchTypes = [
        'eea.climateadapt.aceproject',
        'eea.climateadapt.adaptationoption',
        'eea.climateadapt.casestudy',
        'eea.climateadapt.guidancedocument',
        'eea.climateadapt.indicator',
        'eea.climateadapt.informationportal',
        'eea.climateadapt.mapgraphdataset',
        'eea.climateadapt.organisation',
        'eea.climateadapt.publicationreport',
        'eea.climateadapt.researchproject',
        'eea.climateadapt.tool',
    ]
    results = catalog.searchResults({'portal_type': searchTypes})

    for brain in results:
        obj = aq_self(brain.getObject())

        if not (hasattr(obj, 'special_tags') or hasattr(obj, 'specialtagging')):
            continue

        tags = []
        for attr in ['special_tags', 'specialtagging']:
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
    """ Fix tags in all cover tiles
    """
    # TODO: rename this function, needs better name

    covers = self.portal_catalog.searchResults(
                          portal_type='collective.cover.content')

    for cover in covers:
        cover = cover.getObject()
        if hasattr(cover, '__annotations__'):
            for tile_id in list(cover.__annotations__.keys()):
                tile_id = tile_id.encode()

                if 'plone.tiles.data' in tile_id:
                    tile = cover.__annotations__[tile_id]
                    if 'special_tags' and 'search_text' in tile.keys():
                        tile['special_tags'] = _fix_tags(tile['special_tags'])
                        tile['search_text'] = _fix_tags(tile['search_text'])
                        tile._p_changed = True
                        cover.reindexObject()


def _fix_tags(tags):
    # TODO: rename this function, needs better name
    if isinstance(tags, (list, tuple)):
        tags = [i.replace('-', '_') for i in tags]
    elif tags:
        tags = tags.replace('-', '_')

    return list(set(filter(None, tags)))


def update_to_22(context):
    site = context.getSite()
    catalog = site.portal_catalog

    # Bring back the featured field values from the old database
    ids = ("3402 3403 4704 4706 4202 3323 3505 4102 5301 5901 6301 3503 3504 "
           "3326 3325 4302 4703 3502 4201 3401 3801 4705 3327 4301 6001 4901 "
           "5001 5002 5003 5101 5201 4401 3311 5801 5503 5401 5501 5601 5902 "
           "6201 6101 6202")
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
        if hasattr(b, 'sectors'):
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
        if hasattr(b, 'sectors'):
            if b.sectors is None:
                continue
            else:
                if "INFRASTRUCTURE" in b.sectors:
                    b.sectors.remove("INFRASTRUCTURE")
                    b.sectors = sorted(set(b.sectors + \
                                           ["ENERGY", "TRANSPORT", "BUILDINGS"])
                                       )
                    b.reindexObject()
                    b._p_changed = True

    # assign a measure id for all case studies, it's needed for the /sat map
    _ids = sorted(filter(None, catalog.uniqueValuesFor('acemeasure_id')))
    results = catalog.searchResults(portal_type="eea.climateadapt.casestudy")
    for b in results:
        obj = b.getObject()
        mid = getattr(obj, '_acemeasure_id', None)
        if mid:
            continue
        mid = _ids[-1] + 1
        obj._acemeasure_id = mid
        obj.reindexObject(idxs=['acemeasure_id'])
        _ids.append(mid)


def update_to_23(context):
    site = context.getSite()
    catalog = site.portal_catalog

    MAPPING = {
        'INFRASTRUCTURE': ["ENERGY", "TRANSPORT", "BUILDINGS"],
        'AGRICULTURE': ["FORESTRY", "AGRICULTURE"],
        'AGRI_AND_FOREST': ["FORESTRY", "AGRICULTURE"],
    }

    profiles = catalog.searchResults(
               portal_type="eea.climateadapt.city_profile")
    for b in profiles:
        obj = b.getObject()
        if hasattr(obj, 'key_vulnerable_adaptation_sector'):
            if obj.key_vulnerable_adaptation_sector is None:
                continue

            sectors = obj.key_vulnerable_adaptation_sector
            if isinstance(sectors, str):
                sectors = set(sectors, )
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
