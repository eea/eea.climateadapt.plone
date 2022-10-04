from eea.climateadapt.translation.utils import get_current_language
from plone.app.theming.transform import _Cache
from zope.globalrequest import getRequest
from zope.site.hooks import getSite
from collective.cover.interfaces import ICover
from plone.indexer import indexer
from zope.component import queryAdapter
from collective.cover.interfaces import ISearchableText
from Products.CMFPlone.utils import safe_unicode


def getCache(settings):
    """ The purpose of this is to include the current language in the cache key
    """
    # We need a persistent object to hang a _v_ attribute off for caching.

    registry = settings.__registry__
    caches = getattr(registry, '_v_plone_app_theming_caches', None)
    if caches is None:
        caches = registry._v_plone_app_theming_caches = {}

    plone_site = getSite()
    req = getRequest()
    current_lang = get_current_language(plone_site, req)
    key = "{}/{}".format(plone_site.absolute_url(), current_lang)
    cache = caches.get(key)
    if cache is None:
        cache = caches[key] = _Cache()
    return cache


@indexer(ICover)
def searchableText(obj):
    """Return searchable text to be used as indexer. Includes id, title,
    description and text from Rich Text tiles."""
    text_list = []
    tiles = obj.get_tiles()
    for tile in tiles:
        try:
            tile_obj = obj.restrictedTraverse('@@{0}/{1}'.format(tile['type'], tile['id']))
        except Exception:
            tile_annot_id = 'plone.tiles.data.' + tile['id']
            tile_obj = obj.__annotations__.get(tile_annot_id, None)
        searchable = queryAdapter(tile_obj, ISearchableText)
        if searchable:
            text_list.append(searchable.SearchableText())
    tiles_text = u' '.join(text_list)
    searchable_text = [safe_unicode(entry) for entry in (
        obj.id,
        obj.Title(),
        obj.Description(),
        tiles_text,
    ) if entry]
    searchable_text = u' '.join(searchable_text)
    return searchable_text
