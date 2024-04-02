from eea.climateadapt.interfaces import ICCACountry
from zope.component import adapter, getMultiAdapter
from plone.restapi.interfaces import IExpandableElement
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(ICCACountry, Interface)
class CountryProfile(object):
    """An expander that automatically inserts the HTML rendering of a country profile view
    (the @@country-profile) into the components of country profile serialization
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, **kw):
        view = getMultiAdapter((self.context, self.request), name="country-profile")
        html = view()
        result = {
            "countryprofile": {
                "@id": "{}/@countryprofile".format(self.context.absolute_url()),
                "html": html,
            }
        }

        return result
