from logging import getLogger
from plone.app.event.dx.behaviors import IEventBasic

logger = getLogger("eea.climateadapt")


def install_patches():
    IEventBasic["start"].description = (
        "Date and Time, when the event begins. (When editing an event, "
        "the displayed date and time here is adjusted to your local timezone. "
        "Be careful, as changes may shift the event date and time if it was "
        "originally set in a different timezone)"
    )
    IEventBasic["end"].description = (
        "Date and Time, when the event ends. (When editing an event, "
        "the displayed date and time here is adjusted to your local timezone. "
        "Be careful, as changes may shift the event date and time if it was "
        "originally set in a different timezone)"
    )

    logger.info("Patched IEventBasic descriptions")

