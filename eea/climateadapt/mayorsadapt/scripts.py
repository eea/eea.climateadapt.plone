from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.mayorsadapt.admin import _send_reminders


def send_reminders():
    """ A cron callable script to send reminders

    This should be run through the zope client script running machinery, like so:

    bin/www1 run bin/send_mayoradapt_reminders
    """

    site = get_plone_site()
    _send_reminders(site)
