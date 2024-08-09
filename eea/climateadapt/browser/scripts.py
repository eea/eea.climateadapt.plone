# TODO: this file location is not ideal
from eea.climateadapt.broken_links import compute_broken_links
from eea.climateadapt.browser.external_links import (
    AdapteCCACaseStudyImporter,
    DRMKCImporter,
)
from eea.climateadapt.browser.misc import _archive_news
from eea.climateadapt.scripts import get_plone_site


def import_drmkc():
    """A cron callable script to get DRMKC projects

    This should be run through the zope client script running machinery,:

    bin/zeo_client run bin/import_drmkc
    """
    site = get_plone_site()
    # import pdb; pdb.set_trace()
    drmkc = DRMKCImporter(site)
    drmkc()


def sync_adaptecca_casestudies():
    """A cron callable script to get AdapteCCA case studies

    This should be run through the zope client script running machinery,:

    bin/zeo_client run bin/get_case_studies
    """
    site = get_plone_site()
    adapteCCA = AdapteCCACaseStudyImporter(site)
    adapteCCA()


def get_broken_links():
    """A cron callable script to get data regarding broken links

    This should be run through the zope client script running machinery,:

    bin/zeo_client run bin/get_broken_links
    """
    site = get_plone_site()
    compute_broken_links(site)


def archive_news():
    """A cron callable script which archives news automatically

    This should be run through the zope client script running machinery:

    bin/zeo_client run bin/archive_news
    """
    site = get_plone_site()
    _archive_news(site)
