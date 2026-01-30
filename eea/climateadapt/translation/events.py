import os
import logging
from .core import queue_job
from plone.uuid.interfaces import IUUID

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
        "expected_uid": IUUID(obj, None),
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


def object_removed_handler(obj, event):
    """
    Event handler for ObjectRemovedEvent.
    When a canonical object is removed, delete all its translations.
    """
    if IS_JOB_EXECUTOR:
        return

    # Check if object is canonical (English)
    try:
        if "/en/" not in "/".join(obj.getPhysicalPath()):
            return
    except Exception:
        return

    uids_to_delete = []

    # Use TranslationManager to find translations
    try:
        from plone.app.multilingual.interfaces import ITranslationManager

        tm = ITranslationManager(obj)
        translations = tm.get_translations()

        for lang, trans_obj in translations.items():
            if lang == "en":
                continue

            # Collect UID
            uids_to_delete.append(IUUID(trans_obj))

    except TypeError:
        # Not translatable
        pass
    except Exception as e:
        logger.error(
            "Error in object_removed_handler for %s: %s", obj.absolute_url(), e
        )
        return

    if uids_to_delete:
        queue_job("sync_paths", "delete_translation", {"uids": uids_to_delete})
        logger.info(
            "Queued async deletion for %d translations of %s",
            len(uids_to_delete),
            obj.absolute_url(),
        )
