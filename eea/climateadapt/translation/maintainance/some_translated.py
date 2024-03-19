import logging

from plone.behavior.interfaces import IBehaviorAssignable
from Products.Five.browser import BrowserView
from zope.schema import getFieldsInOrder
from zope.site.hooks import getSite

logger = logging.getLogger("eea.climateadapt")


def admin_some_translated(site, items):
    """Create a list of links to be tested (for translation) for each
    content type
    """
    items = int(items)
    catalog = site.portal_catalog
    portal_types = []
    links = {}
    fields = {}

    res = catalog.searchResults(path="/cca/en")
    count = -1
    for brain in res:
        count += 1
        logger.info(count)
        obj = brain.getObject()

        portal_type = obj.portal_type
        if portal_type not in portal_types:
            portal_types.append(portal_type)
            links[portal_type] = []

            # get behavior fields and values
            behavior_assignable = IBehaviorAssignable(obj)
            _fields = {}
            if behavior_assignable:
                behaviors = behavior_assignable.enumerateBehaviors()
                for behavior in behaviors:
                    for k, val in getFieldsInOrder(behavior.interface):
                        _fields.update({k: val})

            #  get schema fields and values
            for k, val in getFieldsInOrder(obj.getTypeInfo().lookupSchema()):
                _fields.update({k: val})

            fields[portal_type] = [(x, _fields[x]) for x in _fields]

        if len(links[portal_type]) < items:
            links[portal_type].append(obj.absolute_url())

    return {"Content types": portal_types, "Links": links, "fields": fields}


class SomeTranslated(BrowserView):
    """Prepare a list of links for each content type in order to verify
    translation

    Usage: /admin-some-translated?items=10
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return admin_some_translated(getSite(), **kwargs)
