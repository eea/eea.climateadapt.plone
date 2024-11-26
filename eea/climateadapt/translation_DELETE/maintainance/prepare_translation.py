import transaction
from plone.api import content, portal
from Products.Five.browser import BrowserView
from ..core import get_all_objs, create_translation_object
import logging

logger = logging.getLogger("eea.climateadapt")


def execute_trans_script(site, language):
    """Clone the content to be translated"""
    catalog = site.portal_catalog
    english_container = site["en"]
    language_folders = [
        x.id for x in catalog.searchResults(path="/cca", portal_type="LRF")
    ]
    language_folders.remove("en")

    # removed 'frontpage-slides' from lang_independent_objects
    lang_independent_objects = [
        "newsletter",
        "Members",
        "repository",
        "test-baltic",
        "frontpage",
        "admin",
        "more-latest-updates",
        "sandbox",
        "portal_pdf",
        "portal_vocabularies",
        "portal_depiction",
        "dashboard",
        "latest-modifications-on-climate-adapt",
        "covenant-of-mayors-external-website",
        "rss-feed",
        "latest-news-events-on-climate-adapt",
        "specific-privacy-statement-for-climate-adapt",
        "privacy-and-legal-notice",
        "database-items-overview",
        "broken-links",
        "observatory-organisations",
        "observatory-management-group-organisations",
        "indicators-backup",
        "eea-copyright-notice",
        "eea-disclaimer",
        "user-dashboard",
    ]

    # move folders under /en/
    for brain in site.getFolderContents():
        obj = brain.getObject()

        if obj.portal_type != "LRF" and obj.id not in lang_independent_objects:
            content.move(source=obj, target=english_container)

    transaction.commit()
    errors = []
    # get and parse all objects under /en/
    res = get_all_objs(english_container)

    count = 0
    for brain in res:
        logger.info("--------------------------------------------------------")
        logger.info(count)
        count += 1
        if brain.getPath() == "/cca/en" or brain.portal_type == "LIF":
            continue
        obj = brain.getObject()
        try:
            create_translation_object(obj, language)
            logger.info("Cloned: %s" % obj.absolute_url())
        except Exception as err:
            logger.info("Error cloning: %s" % obj.absolute_url())
            if err.message == "Translation already exists":
                continue
            else:
                errors.append(obj)

        if count % 200 == 0:
            logger.info("Processed %s objects" % count)
            transaction.commit()

    transaction.commit()
    logger.info("Errors")
    logger.info(errors)
    logger.info("Finished cloning for language %s" % language)

    return "Finished cloning for language %s" % language


class PrepareTranslation(BrowserView):
    """Clone the content to be available for a new translation
    Usage: /admin-prepare-translation?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return execute_trans_script(portal.getSite(), **kwargs)
