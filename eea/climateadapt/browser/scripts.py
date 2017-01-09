from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.browser.misc import _get_data


def get_broken_links():
    """ A cron callable script to get data regarding broken links

    This should be run through the zope client script running machinery, like so:

    bin/www1 run bin/get_broken_links
    """
    site = get_plone_site()
    _get_data(site)
