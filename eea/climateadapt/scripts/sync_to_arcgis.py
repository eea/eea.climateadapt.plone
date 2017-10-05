#!/usr/bin/env python

""" A script to sync to arcgis

It has multiple entry points that all do different things:
* Call it with its exported console script main():

    bin/www1 run bin/sync_to_arcgis

This connects to Plone to read RabbitMQ server configuration then connects to
RabbitMQ to read all queued messages and process them.
"""

from functools import partial

from eea.climateadapt.sat.handlers import HANDLERS


def _consume_msg(*args, **kw):
    """ Consume RabbitMQ messages. Dispatches messages to proper handler
    """

    resp, props, msg = args[0]
    context = kw['context']

    eventname, uid = msg.split('|', 1)
    HANDLERS[eventname](context, uid)


def main():
    """ Run the sync import process

    This should be run through the zope client script running machinery, like:

    GISPASS="..." bin/www1 run bin/sync_to_arcgis

    It will consume all messages found in the queue and then exit
    """

    from eea.climateadapt.rabbitmq import consume_messages
    from eea.climateadapt.scripts import get_plone_site

    site = get_plone_site()
    consume_messages(
        partial(_consume_msg, context=site),
        queue='eea.climateadapt.casestudies'
    )
