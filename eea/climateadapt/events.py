import logging

import transaction
from DateTime import DateTime
from plone.api import user

logger = logging.getLogger("eea.climateadapt")


def handle_workflow_change(object, event):
    # TODO plone6 is this still needed?
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


def increment_version(object, event):
    if getattr(object, "language", None) != "en":
        return
    version = getattr(object, "_change_version", 0)
    object._change_version = version + 1
    object._p_changed = True


def handle_object_copied_event(object, event):
    # Set the creator to be the current user
    user_id = user.get_current().getId()
    object.creators = (user_id,)
    object._p_changed = True
