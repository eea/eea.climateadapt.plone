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
