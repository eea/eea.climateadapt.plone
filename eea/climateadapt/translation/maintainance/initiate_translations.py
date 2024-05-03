from zope.site.hooks import getSite
from Products.Five.browser import BrowserView

from .translate_obj import translate_obj
import transaction
import logging

logger = logging.getLogger("eea.climateadapt")


def initiate_translations(site, skip=0, version=None, language=None):
    # used for whole-site translation
    skip = int(skip)

    if language is None:
        return "Missing language parameter. (Example: ?language=it)"

    if version is None:
        return "Missing translation version. Status: /admin-translation-status"

    version = int(version)
    catalog = site.portal_catalog
    count = -1
    res = catalog.searchResults(path="/cca/en")
    errors = []
    debug_skip = False
    debug_skip_number = skip  # do not translate first objects

    if skip > 0:
        debug_skip = True
    total_objs = len(res)

    translate_only = False
    only = []  # Example: ['Event', 'cca-event']
    if len(only) > 0:
        translate_only = True  # translate only the specified content types

    for brain in res:
        count += 1

        if debug_skip is True and count < debug_skip_number:
            continue

        if translate_only is True and brain.portal_type not in only:
            continue

        logger.info("--------------------------------------------------------")
        logger.info(count)
        logger.info(total_objs)
        logger.info("--------------------------------------------------------")

        if brain.getPath() == "/cca/en" or brain.portal_type in ["LIF", "LRF"]:
            continue

        obj = brain.getObject()

        try:
            result = translate_obj(obj, language, version)
        except Exception as err:
            result = {"errors": [err]}
            logger.info(err)
            # errors.append(err)
            import pdb

            pdb.set_trace()

        t_errors = result.get("errors", []) if result is not None else []
        if len(t_errors) > 0:
            for error in t_errors:
                if error not in errors:
                    errors.append(error)

        if count % 20 == 0:
            logger.info("Processed %s objects" % count)
            transaction.commit()

    logger.info("DONE")
    logger.info(errors)
    transaction.commit()


class RunTranslation(BrowserView):
    """Translate the contents
    Usage:
    /admin-run-translation?language=it&version=1&skip=1200  -skip 1200 objs
    /admin-run-translation?language=it&version=1
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return initiate_translations(getSite(), **kwargs)
