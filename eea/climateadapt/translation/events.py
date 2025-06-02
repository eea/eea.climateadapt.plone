import logging
from .core import queue_job

logger = logging.getLogger("eea.climateadapt")


def object_modified_handler(obj, event):
    """
    Event handler for ObjectModifiedEvent.
    This handler will be called whenever a content object is modified.
    """

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

    np = "/".join(event.newParent.getPhysicalPath())

    data = {
        "newName": event.newName,
        "oldName": event.oldName,
        "oldParent": op,
        "newParent": np,
    }
    opts = {
        "delay": 100,  # Delay in milliseconds
        "priority": 1,
        "attempts": 3,
        "lifo": False,  # we use FIFO queing
    }

    queue_job("sync_paths", "sync_translated_paths", data, opts)
