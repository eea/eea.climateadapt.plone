""" To be executed after migration is done and tested
"""

import logging
import plone.api

from eea.climateadapt.translation.core import get_all_objs

from plone.app.contenttypes.interfaces import IFolder
from plone.dexterity.interfaces import IDexterityContainer

from .config import IGNORED_CONTENT_TYPES

logger = logging.getLogger("SiteMigrate")
logger.setLevel(logging.INFO)


def is_folderish(obj):
    if (
        IFolder in obj.__provides__.interfaces()
        or IDexterityContainer in obj.__provides__.interfaces()
    ):
        return True
    return False


def post_migration_cleanup(site, request):
    """Remove old index_html leaf page"""
    logger.info("--- START CLEANUP ---")
    brains = get_all_objs(site)

    count = 0

    for brain in brains:
        if brain.portal_type in IGNORED_CONTENT_TYPES:
            continue

        try:
            obj = brain.getObject()
        except Exception:
            continue

        if not is_folderish(obj):
            continue

        default_page = obj.getProperty("default_page")
        if not default_page and "index_html" in obj.contentIds():
            default_page = "index_html"

        if default_page:
            count += 1
            logger.info(default_page)
            default_page_obj = None
            try:
                default_page_obj = obj[default_page]
                print(default_page_obj)
            except (AttributeError, KeyError):
                logger.warning("Ignored %s" % obj.absolute_url())

            if default_page_obj:
                logger.info("Current folder %s" % obj.absolute_url())
                logger.info("Deleting %s" % default_page_obj.absolute_url())
                try:
                    plone.api.content.delete(default_page_obj)
                except Exception:
                    logger.info("Error %s" % default_page_obj.absolute_url())

            try:
                obj.manage_delProperties(["default_page"])
                obj._p_changed = True
                # obj.reindexObject(idxs=['default_page'])
                # TODO: investigate, fix:
                # Module plone.restapi.indexers, line 75,
                # in SearchableText_blocks
                # UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2...
            except Exception:
                pass

            # if count % 10 == 0:
            #     transaction.commit()

    # transaction.commit()
    logger.info("--- Cleanup done ---")
