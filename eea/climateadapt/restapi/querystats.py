from collections import defaultdict
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import adapter, getMultiAdapter
from zope.interface import Interface, implementer
from plone.restapi.serializer.converters import json_compatible


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class QueryStats:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"querystats": {"@id": "%s/@querystats" % self.context.absolute_url()}}
        if not expand:
            return result

        # based on https://github.com/plone/plone.restapi/blob/1771c9c43b63dd0a6b29ab1339b6e8d6330876ab/src/plone/restapi/services/querystringsearch/get.py#L28
        try:
            data = json_body(self.request)
        except DeserializationError as err:
            raise BadRequest(str(err))

        querydata = data.get("query", {})
        query = querydata.get("query", {})
        aggregatefield = data.get("aggregateField", {}).get("value", None)

        if not (query or aggregatefield):
            raise BadRequest("Invalid parameters")

        querybuilder = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )

        querybuilder_parameters = dict(
            query=query,
            brains=True,
        )

        try:
            results = querybuilder(**querybuilder_parameters)
        except KeyError:
            # This can happen if the query has an invalid operation,
            # but plone.app.querystring doesn't raise an exception
            # with specific info.
            raise BadRequest("Invalid query.")

        counts = defaultdict(int)
        for brain in results:
            v = getattr(brain, aggregatefield, None)
            if v:
                if isinstance(v, list):
                    for k in v:
                        counts[k] += 1
                else:
                    counts[v] += 1

        return {"querystats": json_compatible(counts)}


class QueryStatsPost(Service):
    def reply(self):
        querystats = QueryStats(self.context, self.request)
        res = querystats(expand=True)["querystats"]
        print(res)
        return res
