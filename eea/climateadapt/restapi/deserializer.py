# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IFieldDeserializer
from plone.formwidget.geolocation.interfaces import IGeolocationField
from plone.dexterity.interfaces import IDexterityContent
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from zope.component import adapter
from zope.interface import implementer
from plone.formwidget.geolocation.geolocation import Geolocation


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
