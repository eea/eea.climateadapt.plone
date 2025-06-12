"""Upgrade to version 2.0"""

# pylint: disable=line-too-long
import logging
from plone import api
from zope.component import queryMultiAdapter

logger = logging.getLogger("eea.climateadapt")


def migrate_teaser(context):
    """Migrate teaserGrid to gridBlock"""
    portal = api.portal.get()
    view = queryMultiAdapter((portal, context.REQUEST), name="teaser-migrate")
    if view:
        count = view.migrate()
        logger.info("Migrated %s content objects from teaserGrid to gridBlock", count)
    else:
        logger.warning("Migration view 'teaser-migrate' not found")
