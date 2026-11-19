import logging

# import transaction
from DateTime import DateTime
from plone.api import user

logger = logging.getLogger("eea.climateadapt")


def handle_workflow_change(object, event):
    # TODO plone6 is this still needed?
    def updateEffective(object, value):
        object.setEffectiveDate(value)
        object.reindexObject()
        # transaction.commit()

    if event.new_state.title == "Published":
        updateEffective(object, DateTime())
    else:
        if event.status.get("action", None) is not None and (
            event.old_state.title != event.new_state.title
        ):
            updateEffective(object, None)
    return


def increment_version(object, event):
    if getattr(object, "language", None) != "en":
        return
    version = getattr(object, "_change_version", 0)
    object._change_version = version + 1
    object._p_changed = True


#: Users that must not be recorded as the author of a duplicated object. When
#: a copy is made by a script, a content rule or an anonymous traversal there
#: is no real author to attribute, so the copy keeps whatever the original had
#: instead of being credited to a non-existent editor.
NON_AUTHORS = ("", "anonymous_user", "system")


def handle_object_copied_event(object, event):
    """Attribute a duplicated object to the user that duplicated it.

    OFS duplicates content by deep-copying the original, so the copy arrives
    carrying the whole provenance of its source: the original creator, its
    creation date and its effective/expiration dates. Climate-ADAPT editors
    duplicate content instead of adding it from scratch, which meant that
    brand new items kept pointing at the author of the original - in the
    ``Creator`` and ``CreationDate`` catalog indexes, in the REST metadata and
    in the "your item has been published" notification that is sent to the
    creator.

    #281697 / #285994 only reset ``creators``; #309870 asks for the rest of the
    inherited history to be cleared as well.

    ``IObjectCopiedEvent`` is fired by ``OFS.CopySupport`` *before* the copy is
    added to its container, so the values set here are the ones that end up
    being indexed.

    Content fields are deliberately left alone: ``contributors`` and the
    editorial ``publication_date`` (the publication date of the underlying
    material, not of the object) describe the content, not who duplicated it.
    """
    current_user = user.get_current()
    user_id = current_user and current_user.getId()
    if not user_id or user_id in NON_AUTHORS:
        return

    now = DateTime()
    object.creators = (user_id,)
    object.creation_date = now
    object.modification_date = now
    object.setEffectiveDate(None)
    object.setExpirationDate(None)
    object._p_changed = True
