from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)

from eea.climateadapt import CcaAdminMessageFactory as _
from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.directives import form
# from z3c.form.interfaces import IAddForm, IEditForm
from plone.namedfile.field import NamedFile
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
# from plone.schema import JSONField

from zope import schema
from plone.supermodel import model
from plone.namedfile.field import NamedBlobImage
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import provider
from zope.interface import alsoProvides
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField


# TODO: simplify this schema
@provider(IFormFieldProvider)
class IMissionStory(model.Schema, IBlocks):
    """ MissionStory Interface"""
    form.fieldset(
        "mission_story_info",
        label=u"Mission Story Fieldset",
        fields=[
            "climate_impacts",
            "sectors",
            "key_community_systems",
            "spatial_values",
            "funding_programme"
        ],
    )

    form.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_(u"Climate impacts"),
        description=_(
            u"Select one or more climate change impact topics that "
            u"this item relates to."
        ),
        required=False,
        missing_value=[],
        default=None,
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
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
    )

    form.widget(key_community_systems="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    key_community_systems = List(
        title=_(u"Key Community Systems"),
        description=_(
            u"Select one or more key community system that "
            u"this item relates to."
        ),
        required=False,
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.key_community_systems",
        ),
    )

    funding_programme = Choice(
        title=_(u"Funding Programme"),
        required=False,
        vocabulary="eea.climateadapt.funding_programme"
    )

    spatial_values = List(
        title=_(u"Countries"),
        description=_(u"European countries"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )


alsoProvides(IMissionStory["climate_impacts"], ILanguageIndependentField)
alsoProvides(IMissionStory["sectors"], ILanguageIndependentField)
alsoProvides(IMissionStory["key_community_systems"], ILanguageIndependentField)
alsoProvides(IMissionStory["funding_programme"], ILanguageIndependentField)
alsoProvides(IMissionStory["spatial_values"], ILanguageIndependentField)
