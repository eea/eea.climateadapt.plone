from eea.climateadapt import CcaAdminMessageFactory as _
from zope.schema import (Choice, List)
from plone.app.textfield import RichText
from plone.directives import form
from plone.restapi.behaviors import IBlocks
from plone.supermodel import model
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import provider, alsoProvides
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField


@provider(IFormFieldProvider)
class IMissionStory(model.Schema, IBlocks):
    """ MissionStory Interface"""
    form.fieldset(
        "mission_story_info",
        label=u"Mission Story Fieldset",
        fields=[
            "climate_impacts",
            "sectors",
            "key_system",
            "country",
            "climate_threats",
            "funding_programme",
            "key_learnings",
            "region",
            "about_the_region",
            "solution",
            "synopsis",
            "further_information",
            "contact"
        ],
    )

    form.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_(u"Climate Impacts"),
        description=_(
            u"Select one or more climate change impact topics that "
            u"this item relates to."
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",
        ),
    )

    form.widget(climate_threats="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_threats = List(
        title=_(u"Hazard Type"),
        description=_(
            u"Select one or more climate change impact topics that "
            u"this item relates to."
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.climate_threats",
        ),
    )

    form.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(
        title=_(u"Adaptation Sectors"),
        description=_(
            u"Select one or more relevant sector policies that "
            u"this item relates to."
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
    )

    form.widget(key_system="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    key_system = List(
        title=_(u"Key Community Systems"),
        description=_(
            u"Select one or more key community system that "
            u"this item relates to."
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.key_community_systems",
        ),
    )

    funding_programme = Choice(
        title=_(u"Funding Programme"),
        required=False,
        vocabulary="eea.climateadapt.funding_programme"
    )

    country = List(
        title=_(u"Countries"),
        description=_(u"European country"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )

    key_learnings = RichText(
        title=_(u"Key Learnings"),
        required=False,
    )

    about_the_region = RichText(
        title=_(u"About the Region"),
        required=False,
    )

    solution = RichText(
        title=_(u"Solution"),
        required=False,
    )

    synopsis = RichText(
        title=_(u"Synopsis"),
        required=False,
    )

    region = RichText(
        title=_(u"Region"),
        required=False,
    )

    further_information = RichText(
        title=_(u"Further Information"),
        required=False,
    )

    contact = RichText(
        title=_(u"Contact"),
        required=False,
    )


alsoProvides(IMissionStory["climate_impacts"], ILanguageIndependentField)
alsoProvides(IMissionStory["sectors"], ILanguageIndependentField)
alsoProvides(IMissionStory["key_system"], ILanguageIndependentField)
alsoProvides(IMissionStory["climate_threats"], ILanguageIndependentField)
alsoProvides(IMissionStory["region"], ILanguageIndependentField)
alsoProvides(IMissionStory["funding_programme"], ILanguageIndependentField)
alsoProvides(IMissionStory["country"], ILanguageIndependentField)
alsoProvides(IMissionStory["key_learnings"], ILanguageIndependentField)
alsoProvides(IMissionStory["about_the_region"], ILanguageIndependentField)
alsoProvides(IMissionStory["solution"], ILanguageIndependentField)
alsoProvides(IMissionStory["synopsis"], ILanguageIndependentField)
alsoProvides(IMissionStory["further_information"], ILanguageIndependentField)
alsoProvides(IMissionStory["contact"], ILanguageIndependentField)
