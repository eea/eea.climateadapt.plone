from eea.cache import event
from eea.climateadapt.browser.facetedsearch import CCA_TYPES
from plone import api
from plone.app.contentrules.handlers import execute_rules, execute
from plone.app.iterate.dexterity.utils import get_baseline
from plone.app.iterate.event import WorkingCopyDeletedEvent
from zope.annotation.interfaces import IAnnotations
from zope.event import notify


InvalidateCacheEvent = event.InvalidateCacheEvent


def trigger_contentrules(event):
    execute_rules(event)


def trigger_indicator_contentrule(event):
    # context = aq_parent(aq_inner(event.object))
    execute(event.object, event)


def handle_iterate_wc_deletion(object, event):
    """ When a WorkingCopy is deleted, the problem was that the locking was not
    removed. We're manually triggering the IWorkingCopyDeletedEvent because
    the plone.app.iterate handler is registered for IWorkingCopyRelation, a
    derivate of Archetype's relations, which is not used in the dexterity
    implementation.
    """
    try:
        baseline = get_baseline(object)
    except:
        return
    notify(WorkingCopyDeletedEvent(object, baseline, relation=None))


def invalidate_cache_faceted_object_row(obj, evt):
    try:
        uid = obj.UID()
    except Exception:
        # logger.warning("Could not detect UID for obj, %s", obj)
        uid = ''
    key = 'row-' + uid
    notify(InvalidateCacheEvent(raw=False, key=key))


# def set_title_description(obj, event):
#     ''' Sets title to filename if no title
#         was provided.
#         Also sets an empty unicode as description if
#         no description was provided.
#     '''
#     title = obj.title
#
#     if not title:
#         if IRichImage.providedBy(obj):
#             datafield = obj.image
#         else:
#             datafield = obj.file
#
#         if datafield:
#             filename = datafield.filename
#             obj.title = filename
#
#     description = obj.description
#
#     if not description:
#         obj.description = u''

# def invalidate_cache_faceted_sections(obj, evt):
#     """ Invalidate faceted sections cache after cache keys
#     """
#
#     return
#     site = api.portal.getSite()
#     portal_type = obj.portal_type
#
#     print "INVALIDATING CACHE"
#
#     if portal_type not in CCA_TYPES:
#         portal_type = 'CONTENT'
#
#     keys = IAnnotations(site)['cca-search'].get(portal_type, [])
#
#     for key in keys:
#         notify(InvalidateCacheEvent(raw=False, key=key))
#         keys.remove(key)
#
#     IAnnotations(site)['cca-search'][portal_type] = keys


# def invalidate_cache(obj, evt):
#     notify(InvalidateCacheEvent(raw=True))
