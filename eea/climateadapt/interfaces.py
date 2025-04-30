from zope import schema
from zope.interface import Interface


class ICover(Interface):
    """Marker interface for collective.cover.content types to mark them
    after the plone 6 migration to Folder content type
    """


class ICCACountry(Interface):
    """Marker interface for Country Profiles"""


class IClimateAdaptContent(Interface):
    """Marker interface for climate adapt content"""


class IEEAClimateAdaptInstalled(Interface):
    """Browser layer marker interface"""


class IBalticRegionMarker(Interface):
    """A marker interface for Baltic Region pages. They get a special nav menu"""


class ITransnationalRegionMarker(Interface):
    """A marker interface for transnational region pages."""


class IMainTransnationalRegionMarker(Interface):
    """A marker interface for a main transnational region pages."""


class IASTNavigationRoot(Interface):
    """A marker interface for AST tools"""


class ISiteSearchFacetedView(Interface):
    """A marker interface for the /data-and-downloads page"""


class IClimateAdaptSharePage(Interface):
    """A marker interface for the /share-your-info/ pages"""


class IUrbanASTPage(Interface):
    """A marker interface for Urban AST pages"""


class ICountriesRoot(Interface):
    """A marker interface for /countries page"""


class IMayorAdaptRoot(Interface):
    """A marker interface for /mayors-adapt"""


class ICitiesListingsRoot(Interface):
    """A marker interface for /city-profile"""


class IContentRoot(Interface):
    """A marker interface for /content"""


class ITransRegioRoot(Interface):
    """A marker interface for /transnations-regions"""


class INewsEventsLinks(Interface):
    """A marker interface for News, Events, Links content types"""


class IGoogleAnalyticsAPI(Interface):
    """Define settings data structure"""

    credentials_json = schema.Text(
        title="Content of JSON credentials file",
        description="Please use https://developers.google.com/analytics/"
        "devguides/reporting/core/v4/quickstart/service-py"
        " as a guide to generate a new file",
    )

    analytics_app_id = schema.TextLine(
        title="Analytics API View ID",
        description="Use the https://ga-dev-tools.appspot.com/"
        "account-explorer/ to find a view ID ",
    )

    analytics_tracking_id = schema.TextLine(
        title="Analytics Tracking ID",
        description="The tracking ID to send data in the client",
    )


class ICCAContentTypesSettings(Interface):
    """portal_registry ICCAContentTypes settings"""

    fullwidthFor = schema.Tuple(
        title="Fullwidth ContentTypes",
        description="Enable body fullwidth class for the following content-types",
        required=False,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"
        ),
    )
