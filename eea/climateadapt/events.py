from eea.cache import event
from plone import api
from plone.app.contentrules.handlers import execute_rules
from plone.app.iterate.dexterity.utils import get_baseline
from plone.app.iterate.event import WorkingCopyDeletedEvent
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from eea.climateadapt.browser.facetedsearch import CCA_TYPES


InvalidateCacheEvent = event.InvalidateCacheEvent


def trigger_contentrules(event):
    execute_rules(event)


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


def invalidate_cache_faceted_sections(obj, evt):
    """ Invalidate faceted sections cache after cache keys
    """
    return
    site = api.portal.getSite()
    portal_type = obj.portal_type

    print "INVALIDATING CACHE"

    if portal_type not in CCA_TYPES:
        portal_type = 'CONTENT'
    keys = IAnnotations(site)['cca-search'].get(portal_type, [])

    for key in keys:
        notify(InvalidateCacheEvent(raw=False, key=key))
        keys.remove(key)
    IAnnotations(site)['cca-search'][portal_type] = keys


def invalidate_cache(obj, evt):
    notify(InvalidateCacheEvent(raw=True))
