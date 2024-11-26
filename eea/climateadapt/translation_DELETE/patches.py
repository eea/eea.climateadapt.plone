# fix the translation locator to allow it to properly work in async

from plone.api import portal

from plone.app.multilingual.factory import DefaultTranslationLocator as Base
from plone.app.multilingual.interfaces import ITranslationLocator
from zope.interface import implementer
from .core import wrap_in_aquisition


@implementer(ITranslationLocator)
class DefaultTranslationLocator(Base):
    def __call__(self, language):
        """
        Look for the closest translated folder or siteroot
        """
        parent = super(DefaultTranslationLocator, self).__call__(language)
        path = "/".join(parent.getPhysicalPath())
        site = portal.get()
        parent = wrap_in_aquisition(path, site)
        return parent
