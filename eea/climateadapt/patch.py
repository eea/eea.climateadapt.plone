from eea.climateadapt.translation.utils import get_current_language
from plone.app.theming.transform import _Cache
from zope.globalrequest import getRequest
from zope.site.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.ZCTextIndex.ParseTree import ParseError
from plone.app.contentlisting.interfaces import IContentListing


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


# https://github.com/plone/plone.app.search/blob/1.1.x/plone/app/search/browser.py#L33
# Patch the search results to include language filter.
def results(self, query=None, batch=True, b_size=10, b_start=0):
    """ Get properly wrapped search results from the catalog.
    Everything in Plone that performs searches should go through this view.
    'query' should be a dictionary of catalog parameters.
    """
    if query is None:
        query = {}
    if batch:
        query['b_start'] = b_start = int(b_start)
        query['b_size'] = b_size
    query = self.filter_query(query)

    # Customization start -----------------------------------------------------
    languages = ['en', 'fr', 'de', 'it', 'pl', 'es']
    try:
        lang = self.request.form.get('language', None)
        if lang in languages:
            language = lang
        else:
            language = "all"
    except Exception:
        language = "all"

    if language == "all":
        updated_path = "/cca"
    else:
        updated_path = "/cca/" + language

    query['path'] = updated_path
    # Customization end -------------------------------------------------------

    if query is None:
        results = []
    else:
        catalog = getToolByName(self.context, 'portal_catalog')
        try:
            results = catalog(**query)
        except ParseError:
            return []

    results = IContentListing(results)
    if batch:
        results = Batch(results, b_size, b_start)
    return results
