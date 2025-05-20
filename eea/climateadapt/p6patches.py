from logging import getLogger
from plone.app.event.dx.behaviors import IEventBasic
import logging.config

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


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "plone.purgecaching.purger": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Apply the logging configuration
logging.config.dictConfig(logging_config)
