from plone import api
from plone.restapi.interfaces import IExpandableElement, ISerializeToJson
from plone.restapi.services import Service
from zope.component import adapter, getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Siblings(object):
    """siblings object"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "siblings": {"@id": "{}/@siblings".format(self.context.absolute_url())}
        }

        # unline other expandable elements, expand is always True here

        if ("fullobjects" not in self.request.form) and not expand:
            return result

        portal = api.portal.get()

        if self.context is portal:
            return result

        # __import__("pdb").set_trace()
        if "expand" in self.request.form:
            del self.request.form["expand"]
        self.request.form["include_items"] = True

        parent = self.context.aq_parent  # .aq_parent.aq_inner

        serializer = getMultiAdapter((parent, self.request), ISerializeToJson)
        serialized = serializer()
        result["siblings"]["items"] = serialized["items"]

        # query = self._build_query()
        #
        # catalog = getToolByName(self.context, "portal_catalog")
        # brains = catalog(query)
        #
        # batch = HypermediaBatch(self.request, brains)
        #
        # result["items_total"] = batch.items_total
        # if batch.links:
        #     result["batching"] = batch.links
        #
        # if "fullobjects" in list(self.request.form):
        #     result["items"] = getMultiAdapter((brains, self.request), ISerializeToJson)(
        #         fullobjects=True
        #     )["items"]
        # else:
        #     result["items"] = [
        #         getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
        #         for brain in batch
        #     ]

        return result


class SiblingsGet(Service):
    """siblings - get"""

    def reply(self):
        """reply"""
        siblings = Siblings(self.context, self.request)

        return siblings(expand=True)["siblings"]
