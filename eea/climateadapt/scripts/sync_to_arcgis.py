""" A script to sync to arcgis
"""

from eea.climateadapt.scripts import get_plone_site
from eea.rabbitmq.client import RabbitMQConnector
import os


def main():
    """ Run the sync import process

    This should be run through the zope client script running machinery, like so:

    bin/www1 run bin/sync_to_arcgis
    """

    #site = get_plone_site()

    print "done"
