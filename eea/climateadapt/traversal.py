from plone.rest.traverse import RESTWrapper
from zope.component import adapter  # , getUtility
from zope.interface import Interface, implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraversable

# from plone.app.layout.navigation.interfaces import INavigationRoot
# from plone.contentrules.engine.interfaces import IRuleStorage


# @adapter(INavigationRoot, IBrowserRequest)
@adapter(Interface, IBrowserRequest)
@implementer(ITraversable)
class AcquisitionNamespace(object):
    """Used to traverse to a content.

    Traversing to portal/++aq++path/to/something, acquisition-wrapped.
    """

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        base = self.context.restrictedTraverse(name).aq_base

        # handle ++aq++metadata links in the Observatory
        if isinstance(self.context, RESTWrapper):
            context = self.context.context
            base = base.__of__(context)
            self.context.context = base
            return self.context

        self.request.form["observatory_page"] = "1"
        destination = base.__of__(self.context)
        return destination
