from plone.restapi.services.querystring.get import QuerystringGet
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone.app.querystring.registryreader import QuerystringRegistryReader


class CCAQuerystringRegistryReader(QuerystringRegistryReader):
    def parseRegistry(self):
        reg = super().parseRegistry()
        del reg["plone"]["app"]["querystring"]["field"]["Creator"]
        return reg


class CCAQuerystringGet(QuerystringGet):
    """Patch to not expose the Creator field, as it may be too slow"""

    def reply(self):
        registry = getUtility(IRegistry)
        reader = CCAQuerystringRegistryReader(registry, self.request)
        reader.vocab_context = self.context
        result = reader()
        result["@id"] = "%s/@querystring" % self.context.absolute_url()
        return result
