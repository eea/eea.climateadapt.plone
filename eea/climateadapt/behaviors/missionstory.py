from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.widgets.ajaxselect import BetterAjaxSelectWidget
from zope.component import adapter
from zope.interface import alsoProvides, implementer, provider, alsoProvides
from zope.schema import (Choice, List, Tuple, TextLine)
from plone.directives import form
from plone.app.textfield import RichText
from plone.app.widgets.interfaces import IWidgetsLayer
from plone.restapi.behaviors import IBlocks
from plone.supermodel import model
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from z3c.form.widget import FieldWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from plone.autoform import directives

@provider(IFormFieldProvider)
class IMissionStory(model.Schema, IBlocks):
    """ MissionStory Interface"""
    form.fieldset(
        "mission_story_info",
        label=u"Mission Story Fieldset",
        fields=[
            "keywords",
            "climate_impacts",
            "sectors",
            "key_system",
            "country",
            "funding_programme",
            "key_learnings",
            "about_the_region",
            "solution",
            "synopsis",
            "further_information",
            "contact"
        ],
    )

    directives.widget("keywords", vocabulary="eea.climateadapt.keywords")
    keywords = Tuple(
        title=_(u"Keywords"),
        description=_(
            u"Describe and tag this item with relevant keywords. "
            u"Press Enter after writing your keyword. "
        ),
        required=False,
        default=(),
        missing_value=None,
        value_type=TextLine(
            title=u"Single topic",
        ),
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

    further_information = RichText(
        title=_(u"Further Information"),
        required=False,
    )

    contact = RichText(
        title=_(u"Contact"),
        required=False,
    )

@adapter(getSpecification(IMissionStory["keywords"]), IWidgetsLayer)
@implementer(IFieldWidget)
def KeywordsFieldWidget(field, request):
    widget = FieldWidget(field, BetterAjaxSelectWidget(request))
    widget.vocabulary = "eea.climateadapt.keywords"

    return widget

alsoProvides(IMissionStory["climate_impacts"], ILanguageIndependentField)
alsoProvides(IMissionStory['keywords'], ILanguageIndependentField)
alsoProvides(IMissionStory["sectors"], ILanguageIndependentField)
alsoProvides(IMissionStory["key_system"], ILanguageIndependentField)
alsoProvides(IMissionStory["funding_programme"], ILanguageIndependentField)
alsoProvides(IMissionStory["country"], ILanguageIndependentField)
alsoProvides(IMissionStory["key_learnings"], ILanguageIndependentField)
alsoProvides(IMissionStory["about_the_region"], ILanguageIndependentField)
alsoProvides(IMissionStory["solution"], ILanguageIndependentField)
alsoProvides(IMissionStory["synopsis"], ILanguageIndependentField)
alsoProvides(IMissionStory["further_information"], ILanguageIndependentField)
alsoProvides(IMissionStory["contact"], ILanguageIndependentField)
