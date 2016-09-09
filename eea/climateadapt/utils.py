""" Generic utilities
"""

import time
from plone.app.contentrules.handlers import execute_rules


def trigger_contentrules(event):
    execute_rules(event)


def _unixtime(d):
    """ Converts a datetime to unixtime
    """
    try:
        return int(time.mktime(d.utctimetuple()))
    except AttributeError:
        return ""
