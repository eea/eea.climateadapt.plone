from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)

from eea.climateadapt import MessageFactory as _
from plone.app.textfield import RichText
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm

from .indicator import IIndicator


# TODO: simplify this schema
class IC3sIndicator(IIndicator):
    """ Indicator Interface"""

    directives.omitted(IEditForm, "contributor_list")
    directives.omitted(IAddForm, "contributor_list")
    directives.omitted(IEditForm, "other_contributor")
    directives.omitted(IAddForm, "other_contributor")
    directives.omitted(IEditForm, "map_graphs")
    directives.omitted(IAddForm, "map_graphs")
    directives.omitted(IEditForm, "publication_date")
    directives.omitted(IAddForm, "publication_date")

    directives.omitted(IEditForm, "keywords")
    directives.omitted(IAddForm, "keywords")
    directives.omitted(IEditForm, "sectors")
    directives.omitted(IAddForm, "sectors")
    directives.omitted(IEditForm, "climate_impacts")
    directives.omitted(IAddForm, "climate_impacts")
    directives.omitted(IEditForm, "elements")
    directives.omitted(IAddForm, "elements")

    directives.omitted(IEditForm, "websites")
    directives.omitted(IAddForm, "websites")
    directives.omitted(IEditForm, "source")
    directives.omitted(IAddForm, "source")
    directives.omitted(IEditForm, "special_tags")
    directives.omitted(IAddForm, "special_tags")
    # directives.omitted(IEditForm, 'comments')
    # directives.omitted(IAddForm, 'comments')

    directives.omitted(IEditForm, "geographic_information")
    directives.omitted(IAddForm, "geographic_information")

    directives.omitted(IEditForm, "include_in_observatory")
    directives.omitted(IAddForm, "include_in_observatory")
    directives.omitted(IEditForm, "health_impacts")
    directives.omitted(IAddForm, "health_impacts")

    definition_app = RichText(
        title=(u"App definition"),
        description=u"Provide a short description",
        required=False,
    )

    c3s_identifier = TextLine(
        title=_(u"C3S Identifier"), required=True
    )

    overview_app_toolbox_url = TextLine(
        title=_(u"Overview APP Toolbox URL"), required=True
    )

    overview_app_parameters = Text(title=(u"Overview APP parameters"), required=True)

    details_app_toolbox_url = TextLine(
        title=_(u"Details APP Toolbox URL"), required=True
    )

    details_app_parameters = Text(title=(u"Details APP parameters"), required=True)
