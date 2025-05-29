from .core import queue_job


def object_modified_handler(obj, event):
    """
    Event handler for ObjectModifiedEvent.
    This handler will be called whenever a content object is modified.
    """
    op = "/".join(event.oldParent.getPhysicalPath())

    if "/en/" not in op:
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
