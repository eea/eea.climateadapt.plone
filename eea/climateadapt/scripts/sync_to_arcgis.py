""" A script to sync to arcgis
"""

from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.rabbitmq import consume_messages
from functools import partial


def _consume_msg(*args, **kw):
    """ A closure for consumers. If python had curried functions
    """

    resp, props, msg = args[0]
    context = kw['context']

    print "Consuming", msg, context


def main():
    """ Run the sync import process

    This should be run through the zope client script running machinery, like so:

    bin/www1 run bin/sync_to_arcgis

    It will consume all messages found in the queue and then exit
    """

    site = get_plone_site()
    consume_messages(
        partial(_consume_msg, context=site),
        queue='eea.climateadapt.casestudies'
    )

    print "done"
