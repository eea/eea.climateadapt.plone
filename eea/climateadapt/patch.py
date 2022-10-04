from eea.climateadapt.translation.utils import get_current_language
from plone.app.theming.transform import _Cache
from zope.globalrequest import getRequest
from zope.site.hooks import getSite


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
