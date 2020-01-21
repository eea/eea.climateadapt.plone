""" Generic utilities
"""

import time

from DateTime import DateTime


def _unixtime(d):
    """ Converts a datetime to unixtime
    """

    if isinstance(d, DateTime):
        d = d.utcdatetime()

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

    if len(t) > to - 3:
        t = t[:to - 3] + el

    return t
