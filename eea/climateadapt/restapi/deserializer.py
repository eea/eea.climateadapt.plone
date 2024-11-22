# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContent
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.formwidget.geolocation.interfaces import IGeolocationField
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IFieldDeserializer)
@adapter(IGeolocationField, IDexterityContent, IBrowserRequest)
class GeolocationFieldDeserializer(DefaultFieldDeserializer):
    """
        {u'latitude': u'47.058715', u'longitude': u'21.927919041661156'}
        convert coordinates to float when saving the form on edit, to prevent
        Module plone.restapi.deserializer.dxcontent, line 60, in __call__
        BadRequest: [{'field': 'geolocation',
        'message': u'Object is of wrong type.', 'error': 'ValidationError'}]

    """

    def __call__(self, value):
        if value.get('latitude', None) is not None:
            value['latitude'] = float(value['latitude'])

        if value.get('longitude', None) is not None:
            value['longitude'] = float(value['longitude'])

        return Geolocation(value['latitude'], value['longitude'])


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class VolatileSmartField(object):
    """When deserializing block values, delete all block fields that start with `_v_`"""

    order = float("inf")
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        keys = [k for k in list(block.keys()) if k.startswith("_v_")]
        for k in keys:
            del block[k]

        return block
