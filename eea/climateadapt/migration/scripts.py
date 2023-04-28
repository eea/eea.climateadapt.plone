from Products.Five.browser import BrowserView
from plone.api import portal


def _migrate_to_volto(site):
    """ #161595 migration script for Plone 4 to Volto content
    """
    print "WIP migration"
    return "Done"


def migrate_to_volto(site=None):
    if site is None:
        site = get_plone_site()
    _migrate_to_volto(site)


class MigrateToVolto(BrowserView):
    """ A view to manually run the script for migrating to Volto content
    """

    def __call__(self):

        site = portal.get()

        return migrate_to_volto(site)
