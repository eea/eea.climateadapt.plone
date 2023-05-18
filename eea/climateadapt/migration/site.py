""" Migrate content to Volto
"""

import logging

from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.translation.admin import get_all_objs

from .config import IGNORED_CONTENT_TYPES
from .content import migrate_content_to_volto

logger = logging.getLogger('SiteMigrate')
logger.setLevel(logging.WARNING)


def _migrate_to_volto(site, request):
    """ #161595 migration script for Plone 4 to Volto content
    """

    logger.info("--- START CONTENT MIGRATION ---")
    logger.debug("Get the list of items ordered by levels...")
    brains = get_all_objs(site)

    for brain in brains:
        if brain.portal_type in IGNORED_CONTENT_TYPES:
            continue

        obj = brain.getObject()
        migrate_content_to_volto(obj, request)

    logger.info("--- Object migration done ---")


def migrate_to_volto(site=None, request=None):
    """ bin/standalone run bin/migrate_to_volto
    """
    if site is None:
        site = get_plone_site()

    if request is None:
        logger.error("TODO implement fake request")
    else:
        _migrate_to_volto(site, request)
