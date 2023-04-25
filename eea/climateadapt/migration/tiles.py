import logging
from uuid import uuid4
from collections import namedtuple
from plone import api
from plone.app.uuid.utils import uuidToObject
from zope.component.hooks import getSite
from Products.CMFPlone.CatalogTool import sortable_title
from Products.CMFCore.utils import getToolByName


logger = logging.getLogger("eea.climateadapt")

def assigned(tile):
    """Return the list of objects stored in the tile as UUID. If an UUID
    has no object associated with it, removes the UUID from the list.
    :returns: a list of objects.
    """
    # self.set_limit()

    # always get the latest data
    data = tile.get()
    uuids = data.get('uuids')

    results = list()

    if uuids:
        ordered_uuids = [(k, v) for k, v in uuids.items()]
        ordered_uuids.sort(key=lambda x: x[1]["order"])

        for uuid in [i[0] for i in ordered_uuids]:
            obj = uuidToObject(uuid)

            if obj:
                results.append(obj)

            else:
                # maybe the user has no permission to access the object
                # so we try to get it bypassing the restrictions
                catalog = api.portal.get_tool("portal_catalog")
                #brain = catalog.unrestrictedSearchResults(UID=uuid, review_state='published')
                brain = catalog.searchResults(UID=uuid, review_state='published')

                if not brain:
                    # the object was deleted; remove it from the tile
                    obj.remove_item(uuid)
                    logger.debug(
                        "Nonexistent object {0} removed from " "tile".format(uuid)
                    )
    return results

Item = namedtuple(
    "Item", [
        "id", 
        "portal_type", 
        "getId", 
        "UID", 
        "Title",
        "title",
        "Description",
        "meta_type",
        "created",
        "effective",
        "modified",
        "review_state",
        "sortable_title",
    ]
)

def relevant_items(obj, request, tile):
    site = getSite()
    data = tile.get()
    results = []
    items = []

    for item in assigned(tile):
        wftool = getToolByName(item, "portal_workflow")
        state = wftool.getInfoFor(item, "review_state")
        obj_path = item.getPhysicalPath()
        site_path = site.getPhysicalPath()
        path = '/' + '/'.join(obj_path[len(site_path):])
        
        if not item:
            continue
        
        adapter = sortable_title(item)
        st = adapter()
        o = Item(
            path,
            item.portal_type,
            item.getId(),
            item.UID(),
            item.Title(),
            item.Title(),
            item.Description(),
            item.meta_type,
            item.created(),
            item.effective(),
            item.modified(),
            state,
            st,
        )
        items.append(o)
    
    combine = data.get("combine_results", False)

    if not combine:
        if items:
            if data.get("sortBy", "") == "NAME":
                items = sorted(items, key=lambda o: o.sortable_title)


    for item in items:
        o = {
            '@id': str(uuid4()),
            'item_title': item.Title,
            'link': path,
            'source': [{
                "@id": path,
                "@type": item.portal_type,
                "getId": item.getId,
                "UID": item.UID,
                "Title": item.Title,
                "title": item.Title,
                "meta_type": item.meta_type,
                "Description": item.Description,
                "created": item.created,
                "effective": item.effective,
                "modified": item.modified,
                "review_state": item.review_state,
            }]
        }
        
        results.append(o)

    return results