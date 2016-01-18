from zope.interface import Interface


class IEEAClimateAdaptInstalled(Interface):
    """ Browser layer marker interface
    """


class IBalticRegionMarker(Interface):
    """ A marker interface for Baltic Region pages. They get a special nav menu
    """


class ITransnationalRegionMarker(Interface):
    """ A marker interface for transnational region pages.
    """


class IASTNavigationRoot(Interface):
    """ A marker interface for AST tools
    """


class ISiteSearchFacetedView(Interface):
    """ A marker interface for the /data-and-downloads page
    """
