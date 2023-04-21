from eea.climateadapt.translation.utils import get_current_language
from plone.app.theming.transform import _Cache
from zope.globalrequest import getRequest
from zope.schema.vocabulary import SimpleTerm
from zope.site.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.ZCTextIndex.ParseTree import ParseError
from plone.app.contentlisting.interfaces import IContentListing
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.summary import (
    NON_METADATA_ATTRIBUTES,
    DEFAULT_METADATA_FIELDS,
)


def getCache(settings):
    """The purpose of this is to include the current language in the cache key"""
    # We need a persistent object to hang a _v_ attribute off for caching.

    registry = settings.__registry__
    caches = getattr(registry, "_v_plone_app_theming_caches", None)
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
# Refs #159767 - Patch the search results to include language filter.
def results(self, query=None, batch=True, b_size=10, b_start=0):
    """Get properly wrapped search results from the catalog.
    Everything in Plone that performs searches should go through this view.
    'query' should be a dictionary of catalog parameters.
    """
    if query is None:
        query = {}
    if batch:
        query["b_start"] = b_start = int(b_start)
        query["b_size"] = b_size
    query = self.filter_query(query)

    # Customization start -----------------------------------------------------
    try:
        default_language = self.request.cookies.get("I18N_LANGUAGE", "en")
    except Exception:
        default_language = "en"

    languages = ["en", "fr", "de", "it", "pl", "es"]
    try:
        lang = self.request.form.get("language", default_language)
        if lang in languages:
            language = lang
        else:
            language = "all"
    except Exception:
        language = default_language

    if language == "all":
        updated_path = "/cca"
    else:
        updated_path = "/cca/" + language

    if query is None:
        query = {}
    query["path"] = updated_path
    # Customization end -------------------------------------------------------

    if query is None:
        results = []
    else:
        catalog = getToolByName(self.context, "portal_catalog")
        try:
            results = catalog(**query)
        except ParseError:
            return []

    results = IContentListing(results)
    if batch:
        results = Batch(results, b_size, b_start)
    return results


# https://github.com/plone/plone.restapi/blob/7.x.x/src/plone/restapi/serializer/summary.py#L72
# Refs #162035 - Make internal ZCatalog compatible with Plone 6
def metadata_fields(self):
    # The override is based on
    # https://github.com/plone/plone.restapi/blob/master/src/plone/restapi/serializer/summary.py
    # keeping the 7.x.x DEFAULT_METADATA_FIELDS and NON_METADATA_ATTRIBUTES
    query = self.request.form
    if not query:
        # maybe its a POST request
        query = json_body(self.request)
    additional_metadata_fields = query.get("metadata_fields", [])
    if not isinstance(additional_metadata_fields, list):
        additional_metadata_fields = [additional_metadata_fields]
    additional_metadata_fields = set(additional_metadata_fields)

    if "_all" in additional_metadata_fields:
        fields_cache = self.request.get("_summary_fields_cache", None)
        if fields_cache is None:
            catalog = getToolByName(self.context, "portal_catalog")
            fields_cache = set(catalog.schema()) | NON_METADATA_ATTRIBUTES
            self.request.set("_summary_fields_cache", fields_cache)
        additional_metadata_fields = fields_cache

    return DEFAULT_METADATA_FIELDS | additional_metadata_fields


# Refs #248978
def getTerm(self, userid):
    try:
        token = userid.encode("utf-8")
    except:
        token = userid

    fullname = userid
    user = self._users.getUserById(userid, None)
    if user:
        fullname = user.getProperty('fullname', None) or userid
    
    return SimpleTerm(userid, token, fullname)
