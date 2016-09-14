""" Generic utilities
"""

import time

def _unixtime(d):
    """ Converts a datetime to unixtime
    """
    try:
        return int(time.mktime(d.utctimetuple()))
    except AttributeError:
        return ""
