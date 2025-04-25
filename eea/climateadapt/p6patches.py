from logging import getLogger
from plone.app.event.dx.behaviors import IEventBasic

logger = getLogger("eea.climateadapt")


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
