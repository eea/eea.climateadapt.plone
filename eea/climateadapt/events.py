import logging

import transaction
from DateTime import DateTime
from plone.api.user import get_current
from plone.app.contentrules.handlers import execute, execute_rules
from plone.app.iterate.dexterity.utils import get_baseline
from plone.app.iterate.event import WorkingCopyDeletedEvent
from plone.dexterity.interfaces import IDexterityContent
from zc.relation.interfaces import ICatalog
from zope import component
from zope.component import adapter
from zope.event import notify
from zope.globalrequest import getRequest
from zope.lifecycleevent.interfaces import IObjectAddedEvent

from eea.cache import event

logger = logging.getLogger("eea.climateadapt")

InvalidateCacheEvent = event.InvalidateCacheEvent


def trigger_contentrules(event):
    execute_rules(event)


def trigger_indicator_contentrule(event):
    # context = aq_parent(aq_inner(event.object))
    execute(event.object, event)


def handle_iterate_wc_deletion(object, event):
    """When a WorkingCopy is deleted, the problem was that the locking was not
    removed. We're manually triggering the IWorkingCopyDeletedEvent because
    the plone.app.iterate handler is registered for IWorkingCopyRelation, a
    derivate of Archetype's relations, which is not used in the dexterity
    implementation.
    """
    try:
        baseline = get_baseline(object)
    except:
        return
    try:
        notify(WorkingCopyDeletedEvent(object, baseline, relation=None))
    except:
        logger.exception("Exception in handling iterate working copy deletion")
        pass


def invalidate_cache_faceted_object_row(obj, evt):
    try:
        uid = obj.UID()
    except Exception:
        # logger.warning("Could not detect UID for obj, %s", obj)
        uid = ""
    key = "row-" + uid
    notify(InvalidateCacheEvent(raw=False, key=key))


def deletion_confirmed():
    """Check if we are in the context of a delete confirmation event.
    We need to be sure we're in the righ event to process it, as
    `IObjectRemovedEvent` is raised up to three times: the first one
    when the delete confirmation window is shown; the second when we
    select the 'Delete' button; and the last, as part of the
    redirection request to the parent container. Why? I have absolutely
    no idea. If we select 'Cancel' after the first event, then no more
    events are fired.
    """
    request = getRequest()
    folder_delete = "folder_delete" in request.URL
    is_delete_confirmation = "delete_confirmation" in request.URL
    zmi_delete = "manage_delObjects" in request.URL
    is_post = request.REQUEST_METHOD == "POST"
    # form_being_submitted = 'form.submitted' in request.form
    # return (is_delete_confirmation and is_post and form_being_submitted) \
    #     or (folder_delete and is_post)
    return (
        (is_delete_confirmation and is_post)
        or (folder_delete and is_post)
        or (zmi_delete and is_post)
    )


def remove_broken_relations(obj, event):
    """Event handler to remove broken relations when an object is
    deleted/moved/added/modified
    """
    if not deletion_confirmed():
        return
    else:
        request = obj.REQUEST

        catalog = component.queryUtility(ICatalog)
        if catalog is None:
            return

        for relation in list(catalog.findRelations({"to_id": None})):
            catalog.unindex(relation)
            if relation in relation.from_object.relatedItems:
                relation.from_object.relatedItems.remove(relation)
            relation.from_object._p_changed = 1
            relation.from_object.reindexObject()

        # transaction.commit()
        if request.form.get("ajax_load", None):
            if isinstance(request.form["ajax_load"], list):
                request.form["ajax_load"].pop()
                request.form["ajax_load"] = request.form["ajax_load"][0]
        return


def handle_workflow_change(object, event):
    def updateEffective(object, value):
        object.setEffectiveDate(value)
        object.reindexObject()
        transaction.commit()

    if event.new_state.title == "Published":
        updateEffective(object, DateTime())
    else:
        if event.status.get("action", None) is not None and (
            event.old_state.title != event.new_state.title
        ):
            updateEffective(object, None)
    return


@adapter(IDexterityContent, IObjectAddedEvent)
def fix_creators(obj, event):
    current_user = get_current()
    if current_user:
        user_id = current_user.getId()
        obj.creators = [user_id]
        logger.info(
            "Fix user for copy/pasted object to %s for %s",
            user_id,
            "/".join(obj.getPhysicalPath()),
        )


# from zope.annotation.interfaces import IAnnotations
# from eea.climateadapt.browser.facetedsearch import CCA_TYPES
# from plone import api


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
