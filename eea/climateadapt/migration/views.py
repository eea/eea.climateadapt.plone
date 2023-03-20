from eea.climateadapt.migration.interfaces import IMigrateToVolto
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


class MigrateContent(BrowserView):
    def __call__(self):
        migrate = getMultiAdapter((self.context, self.request), IMigrateToVolto)
        migrate()

        return "ok"
