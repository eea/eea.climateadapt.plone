import os
import logging
from .core import queue_job

logger = logging.getLogger("eea.climateadapt")

env = os.environ.get

IS_JOB_EXECUTOR = env("IS_JOB_EXECUTOR", False)


def object_modified_handler(obj, event):
    """
    Event handler for ObjectModifiedEvent.
    This handler will be called whenever a content object is modified.
    """

    if IS_JOB_EXECUTOR:
        # obj.REQUEST.tg = "notg"
        return

    try:
        op = "/".join(event.oldParent.getPhysicalPath())
    except Exception:
        logger.warning(
            "Could not identify old parent for %s", "/".join(
                obj.getPhysicalPath())
        )
        return

    try:
        np = "/".join(event.newParent.getPhysicalPath())
    except Exception:
        logger.warning(
            "Could not identify new parent for %s", "/".join(
                obj.getPhysicalPath())
        )
        return

    logger.info(
        "Object moved %s -> %s (%s -> %s)",
        op,
        np,
        event.oldName,
        event.newName,
    )

    if not ("/en/" in op or op.endswith("/en")):
        return

    # Deduplication check
    if hasattr(obj.REQUEST, "cca_sync_paths_triggered"):
        return
    
    obj.REQUEST.cca_sync_paths_triggered = True

    np = "/".join(event.newParent.getPhysicalPath())

    try:
        import traceback
        tb = traceback.format_stack()
    except Exception:
        tb = "Could not get traceback"

    try:
        from plone import api
        user = api.user.get_current()
        user_id = user.getId() if user else "system/unknown"
    except Exception:
        user_id = "error_getting_user"

    data = {
        "newName": event.newName,
        "oldName": event.oldName,
        "oldParent": op,
        "newParent": np,
        "debug_info": {
            "traceback": tb,
            "user": user_id,
            "event_trigger": "object_modified_handler"
        }
    }
    opts = {
        "delay": 100,  # Delay in milliseconds
        "priority": 1,
        "attempts": 3,
        "lifo": False,  # we use FIFO queing
    }

    queue_job("sync_paths", "sync_translated_paths", data, opts)
