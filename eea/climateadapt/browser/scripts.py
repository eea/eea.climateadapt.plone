from eea.climateadapt.browser.misc import _archive_news, compute_broken_links
from eea.climateadapt.scripts import get_plone_site


def get_broken_links():
    """ A cron callable script to get data regarding broken links

    This should be run through the zope client script running machinery,:

    bin/www1 run bin/get_broken_links
    """
    site = get_plone_site()
    compute_broken_links(site)


def archive_news():
    """ A cron callable script which archives news automatically

    This should be run through the zope client script running machinery:

    bin/www1 run bin/archive_news
    """
    site = get_plone_site()
    _archive_news(site)
