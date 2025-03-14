from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from zope.interface import alsoProvides
from zope.schema import (
    # URI,
    # Bool,
    Choice,
    Date,
    # Datetime,
    # Int,
    List,
    Text,
    TextLine,
    # Tuple,
)

from eea.climateadapt import CcaAdminMessageFactory as _

from .indicator import IIndicator


# TODO: simplify this schema
class IC3sIndicator(IIndicator):
    """Indicator Interface"""

    # directives.omitted(IEditForm, "contributor_list")
    # directives.omitted(IAddForm, "contributor_list")
    directives.omitted(IEditForm, "other_contributor")
    directives.omitted(IAddForm, "other_contributor")
    directives.omitted(IEditForm, "map_graphs")
    directives.omitted(IAddForm, "map_graphs")
    # directives.omitted(IEditForm, "publication_date")
    # directives.omitted(IAddForm, "publication_date")

    # directives.omitted(IEditForm, "keywords")
    # directives.omitted(IAddForm, "keywords")
    # directives.omitted(IEditForm, "sectors")
    # directives.omitted(IAddForm, "sectors")
    # directives.omitted(IEditForm, "climate_impacts")
    # directives.omitted(IAddForm, "climate_impacts")
    # directives.omitted(IEditForm, "elements")
    # directives.omitted(IAddForm, "elements")

    # directives.omitted(IEditForm, "websites")
    # directives.omitted(IAddForm, "websites")
    # directives.omitted(IEditForm, "source")
    # directives.omitted(IAddForm, "source")
    # directives.omitted(IEditForm, "special_tags")
    # directives.omitted(IAddForm, "special_tags")
    # directives.omitted(IEditForm, 'comments')
    # directives.omitted(IAddForm, 'comments')

    # directives.omitted(IEditForm, "geographic_information")
    # directives.omitted(IAddForm, "geographic_information")

    # directives.omitted(IEditForm, "include_in_observatory")
    # directives.omitted(IAddForm, "include_in_observatory")
    # directives.omitted(IEditForm, "health_impacts")
    # directives.omitted(IAddForm, "health_impacts")

    indicator_title = TextLine(title=_("Indicator title"), required=False)

    definition_app = RichText(
        title=("App definition"),
        description="Provide a short description",
        required=False,
    )

    c3s_identifier = TextLine(title=_("C3S Identifier"), required=True)

    overview_app_toolbox_url = TextLine(
        title=_("Overview APP Toolbox URL"), required=False
    )

    overview_app_toolbox_url_v2 = TextLine(
        title=_("Overview APP Toolbox URL V2"),
        description="used for items after ecde_identifier option",
        required=False,
    )

    overview_app_toolbox_url_v2 = TextLine(
        title=_("Overview APP Toolbox URL V2"),
        description="used for items after ecde_identifier option",
        required=False,
    )

    overview_app_parameters = Text(
        title=("Overview APP parameters"), required=True)

    overview_app_ecde_identifier = TextLine(
        title=_("Overview APP ECDE Identifier"), required=True
    )

    overview_app_ecde_identifier = TextLine(
        title=_("Overview APP ECDE Identifier"), required=True
    )

    details_app_toolbox_url = TextLine(
        title=_("Details APP Toolbox URL"), required=False
    )

    details_app_parameters = Text(
        title=("Details APP parameters"), required=False)

    sectors = List(
        title=_("Sectors"),
        description=_(
            "Select one or more relevant sector policies that this item relates to."
        ),
        required=False,
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
    )

    climate_impacts = List(
        title=_("Climate impacts"),
        description=_(
            "Select one or more climate change impact topics that this item relates to."
        ),
        required=False,
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",
        ),
    )

    publication_date = Date(
        title=_("Date of item's publication"),
        description="The date refers to the latest date of publication of "
        "the item."
        " Please use the Calendar icon to add day/month/year. If you want to "
        'add only the year, please select "day: 1", "month: January" '
        "and then the year",
        required=False,
    )


alsoProvides(IC3sIndicator["c3s_identifier"], ILanguageIndependentField)
alsoProvides(IC3sIndicator["overview_app_toolbox_url"],
             ILanguageIndependentField)
alsoProvides(
    IC3sIndicator["overview_app_toolbox_url_v2"], ILanguageIndependentField)
alsoProvides(IC3sIndicator["overview_app_parameters"],
             ILanguageIndependentField)
alsoProvides(IC3sIndicator["details_app_toolbox_url"],
             ILanguageIndependentField)
alsoProvides(IC3sIndicator["details_app_parameters"],
             ILanguageIndependentField)
alsoProvides(IC3sIndicator["sectors"], ILanguageIndependentField)
alsoProvides(IC3sIndicator["climate_impacts"], ILanguageIndependentField)
alsoProvides(IC3sIndicator["publication_date"], ILanguageIndependentField)
alsoProvides(IC3sIndicator["map_graphs"], ILanguageIndependentField)
