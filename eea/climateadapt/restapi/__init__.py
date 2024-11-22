""" plone.restapi customizations
"""

from plone.app.textfield.interfaces import IRichTextValue
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.serializer.converters import json_compatible
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.interface import implementer


@adapter(int)
@implementer(IJsonCompatible)
def long_converter(value):
    return safe_unicode(str(value))


@adapter(Geolocation)
@implementer(IJsonCompatible)
def geolocation_converter(value):
    return json_compatible(vars(value))


@adapter(IRichTextValue)
@implementer(IJsonCompatible)
def richtext_value_converter(value):
    return value and value.output or ""
