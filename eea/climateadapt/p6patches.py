from plone.restapi.cache import paths
from plone.cachepurging.purger import logger as purgeLogger
from plone.app.event.dx.behaviors import IEventBasic
import logging


purgeLogger.setLevel(logging.DEBUG)

logger = logging.getLogger("eea.climateadapt")


def install_patches():
    IEventBasic["start"].description = (
        "Date and time when the event begins (in your local timezone). "
        "For example, if you're in Copenhagen and creating an event for Athens, "
        "use Copenhagen time, not Athens time."
    )
    IEventBasic["end"].description = (
        "Date and time when the event ends (in your local timezone). "
        "For example, if you're in Copenhagen and creating an event for Athens, "
        "use Copenhagen time, not Athens time."
    )
    logger.info("Patched IEventBasic descriptions")

    paths.CONTEXT_ENDPOINTS = [
        "?expand=translations,subsite,breadcrumbs,navigation,actions&expand.navigation.depth=3",
        "/?expand=translations,subsite,breadcrumbs,navigation,actions&expand.navigation.depth=3",
    ]

    logger.info("plone.restapi cache purging paths were setup for CCA")
