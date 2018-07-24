""" Interfaces
"""
from zope import schema

from zope.interface import Interface
from zope.schema import TextLine

class IEEAContentTypesSettings(Interface):
    """ portal_registry ICCAContentTypes settings
    """

    fullwidthFor = schema.Tuple(
        title=_(u"Fullwidth ContentTypes"),
        description=_(u"Enable body fullwidth class for the "
                      "following content-types"),
        required=False,
        default=('GIS Application',),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes")
    )
