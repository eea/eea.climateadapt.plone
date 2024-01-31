""" Utilities to convert to streamlined HTML and from HTML to volto blocks

The intention is to use eTranslation as a service to translate a complete Volto page with blocks
by first converting the blocks to HTML, then ingest and convert that structure back to Volto blocks
"""

from zope.schema import getFieldsInOrder
from plone.dexterity.utils import iterSchemata
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField

from Products.Five.browser import BrowserView


class ContentToHtml(BrowserView):
    def __call__(self):
        obj = self.context
        fields = {}

        for schema in iterSchemata(obj):
            for k, v in getFieldsInOrder(schema):
                if ILanguageIndependentField.providedBy(v):
                    continue
                print(schema, k)
                fields[k] = v

        # __import__("pdb").set_trace()
        # typeinfo = obj.getTypeInfo()
        # for behavior in typeinfo.behaviors:
        #     pass
        # schema = typeinfo.lookupSchema()
        # __import__("pdb").set_trace()

        return fields
