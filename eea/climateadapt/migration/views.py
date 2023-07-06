import logging

from eea.climateadapt.migration.interfaces import IMigrateToVolto
from plone.api import portal
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from .fixes import fix_site
from .site import migrate_to_volto
from .cleanup import post_migration_cleanup

logger = logging.getLogger("eea.climateadapt")

edw_logger = logging.getLogger("edw.logger")
edw_logger.setLevel(logging.ERROR)


class MigrateContent(BrowserView):
    def __call__(self):
        migrate = getMultiAdapter(
            (self.context, self.request), IMigrateToVolto)
        try:
            migrate()
        except Exception:
            logger.exception("Error in migrator")

        return "ok"


class MigrateSiteToVolto(BrowserView):
    """ A view to manually run the script for migrating to Volto content
    """

    def __call__(self):

        site = portal.get()
        fix_site(site)

        if self.request.form.get('migrate') == "0":
            return "ok"

        migrate_to_volto(site, self.request)
        # raise ValueError
        return "ok"


class PostMigrationCleanup(BrowserView):
    """ Remove old index_html leaf pages after migration
    """

    def __call__(self):
        site = portal.get()
        post_migration_cleanup(site)

        return "ok"
