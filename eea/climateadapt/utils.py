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


def shorten(t, to=254):
    """ Shortens text and adds elipsis
    """

    if isinstance(t, unicode):
        el = u'...'
    else:
        el = '...'
    if len(t) > to-3:
        t = t[:to-3] + el
    return t

