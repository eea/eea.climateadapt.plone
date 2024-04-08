from eea.climateadapt import CcaAdminMessageFactory as _
from zope.schema import Choice, List
from plone.directives import form
from plone.restapi.behaviors import IBlocks
from plone.supermodel import model
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from zope.interface import alsoProvides, implementer, provider, alsoProvides


@provider(IFormFieldProvider)
class IMissionFundingCCA(model.Schema, IBlocks):
    """MissionFundingCCA Interface"""

    form.fieldset(
        "mission_funding_metadata",
        label="Metadata",
        fields=[
            "sectors",
            "country",
        ],
    )

    form.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(
        title=_("Adaptation Sectors"),
        description=_(
            "Select one or more relevant sector policies that " "this item relates to."
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
    )

    country = List(
        title=_("Countries"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )


alsoProvides(IMissionFundingCCA["sectors"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["country"], ILanguageIndependentField)
