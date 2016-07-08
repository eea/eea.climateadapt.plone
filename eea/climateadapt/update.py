from Acquisition import aq_self


def fixtiles(context):
    if context.readDataFile('eea.climateadapt.update.txt') is None:
        return

    site = context.getSite()

    results = search_catalog(site)

    for result in results:
        obj = result.getObject()
        if hasattr(aq_self(obj), 'special_tags'):
            obj.special_tags = replt(obj.special_tags)
        elif hasattr(obj, 'specialtagging'):
            obj.special_tags = obj.specialtagging
            obj.special_tags = replt(obj.special_tags)
        else:
            # print "Not changed ", obj.Title()
            pass

        obj.reindexObject()

    modify_covers(site)

    return self.index()


def modify_covers(self):
    """ Function to modify the tiles in each cover
    """

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
                        tile['special_tags'] = replt(tile['special_tags'])
                        tile['search_text'] = replt(tile['search_text'])
                        tile._p_changed = True
                        cover.reindexObject()


def replt(word):
    """ Function to replace the text
    """

    if isinstance(word, (list, tuple)):
        word = [i.replace('-', '_') for i in word]
    elif word is not None and word is not '':
        word = word.replace('-', '_')
    else:
        pass

    return word


def search_catalog(self):
    """  Perform a catalog search
    """
    catalog = self.portal_catalog

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

    return results
