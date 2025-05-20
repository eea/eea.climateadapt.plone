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
