from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.browser.misc import _get_data, _archive_news


def get_broken_links():
    """ A cron callable script to get data regarding broken links

    This should be run through the zope client script running machinery, like so:

    bin/www1 run bin/get_broken_links
    """
    site = get_plone_site()
    _get_data(site)


def archive_news():
    """ A cron callable script which archives news automatically

    This should be run through the zope client script running machinery, like so:

    bin/www1 run bin/archive_news
    """
    site = get_plone_site()
    _archive_news(site)
