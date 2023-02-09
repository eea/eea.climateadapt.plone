""" plone.restapi customizations
"""
from plone.restapi.interfaces import IJsonCompatible
from zope.component import adapter
from zope.interface import implementer
from Products.CMFPlone.utils import safe_unicode
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.restapi.serializer.converters import json_compatible


@adapter(long)
@implementer(IJsonCompatible)
def long_converter(value):
    return safe_unicode(str(value))


@adapter(Geolocation)
@implementer(IJsonCompatible)
def geolocation_converter(value):
    return json_compatible(vars(value))
