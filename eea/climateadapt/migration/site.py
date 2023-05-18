""" Migrate content to Volto
"""

import logging

from eea.climateadapt.migration.interfaces import IMigrateToVolto
from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.translation.admin import get_all_objs
from plone.api.content import get_state
from plone.dexterity.interfaces import IDexterityContent
from zope.component import queryMultiAdapter

logger = logging.getLogger('eea.climateadapt')

IGNORED_CONTENT_TYPES = [
    # TODO:
    'Document',
    'Event',

    'Image', 'LRF', 'LIF', 'Collection', 'Link', 'DepictionTool', 'Subsite',

]

# TODO: Document


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
        url = obj.absolute_url(relative=True)

        if '/mission/' in (url + '/'):
            continue

        if not IDexterityContent.providedBy(obj):
            logger.debug("Ignoring %s, not a dexterity content", url)
            continue

        try:
            state = get_state(obj)
        except Exception:
            logger.warn("Unable to get review state for %s", url)
        else:
            if state == 'archived':
                logger.debug("Skip migrating %s as it's archived", url)
                continue

        logger.info("Migrating %s" % url)

        migrate = queryMultiAdapter((obj, request), IMigrateToVolto)

        if migrate is None:
            import pdb
            pdb.set_trace()
            logger.warning("No migrator for %s", url)
            continue

        try:
            migrate()
        except Exception:
            logger.exception("Error in migrating %s" % url)

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
