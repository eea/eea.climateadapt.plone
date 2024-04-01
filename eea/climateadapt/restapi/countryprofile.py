from eea.climateadapt.interfaces import ICCACountry
from zope.component import adapter, getMultiAdapter
from plone.restapi.interfaces import IExpandableElement
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(ICCACountry, Interface)
class CountryProfile(object):
    """siblings object"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, **kw):
        result = {
            "countryprofile": {
                "@id": "{}/@countryprofile".format(self.context.absolute_url())
            }
        }

        view = getMultiAdapter((self.context, self.request), name="country-profile")
        html = view()
        result["countryprofile"] = html

        return result
