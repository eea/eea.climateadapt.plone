from collective.excelexport.exportables.base import BaseExportableFactory
from collective.excelexport.exportables.dexterityfields import \
    BaseFieldRenderer
from zope.component import adapts
from zope.interface import Interface
from zope.schema.interfaces import IDatetime, IList, IText, ITextLine, ITuple

from eea.climateadapt.schema import AbsoluteUrl, PortalType, Uploader, Year
from plone.api import content, portal
from plone.dexterity.interfaces import IDexterityFTI
from plone.formwidget.geolocation.interfaces import IGeolocationField
from Products.CMFPlone.utils import safe_unicode
from z3c.form.interfaces import NO_VALUE
from z3c.relationfield.interfaces import IRelationList


class BaseRenderer(object):
    """
    """

    def render_value(self, obj):
        value = self.get_value(obj)

        if value == NO_VALUE:
            return None
        else:
            return value

    def render_collection_entry(self, obj, value):
        """Render a value element if the field is a sub field of a collection
        """

        return safe_unicode(value or "")

    def render_style(self, obj, base_style):
        """Gets the style rendering of the
        base_style is the default style of a cell for content
        You can modify base_style, it's already a copy, and return it.
        You can return a Style object with headers and content attributes too.
        """

        return base_style

class ObjectStateRenderer(BaseRenderer):
    """ Object state: published/unpublished renderer
    """

    def get_value(self, obj):
        return content.get_state(obj)

    def render_header(self):
        return "review state"

class CreatorRenderer(BaseRenderer):
    """ Item creator renderer
    """
    def get_value(self, obj):
        return obj.Creator()

    def render_header(self):
        return 'creator'

class MetadataExportablesFactory(BaseExportableFactory):
    """Get fields content schema
    """
    adapts(IDexterityFTI, Interface, Interface)
    weight = 100

    def get_exportables(self):
        exportables = [
            ObjectStateRenderer(),
            CreatorRenderer()
        ]

        return exportables


class DateTimeFieldRenderer(BaseFieldRenderer):
    """ Datetime field adapter for excel export"""
    adapts(IDatetime, Interface, Interface)

    def _get_text(self, value):
        return portal.get_localized_time(datetime=value)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)

        if not value or value == NO_VALUE:
            return ""

        text = safe_unicode(self._get_text(value))

        return text


class RelationListFieldRenderer(BaseFieldRenderer):
    """ Renderer for related items """
    adapts(IRelationList, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """ Gets the value to render in excel file from content value
        """

        value = self.get_value(obj)

        if not value or value == NO_VALUE:
            return ""

        text = safe_unicode(self._get_text(value))

        new_text = []

        for item in text:
            if item.to_object is not None:
                new_text.append(item.to_object.Title() + ';\n')
            else:
                pass

        return new_text


class ListFieldRenderer(BaseFieldRenderer):
    """ List field adapter for excel export"""
    adapts(IList, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """

        value = self.get_value(obj)

        if not value or value == NO_VALUE:
            return ""

        text = safe_unicode(self._get_text(value))

        if isinstance(text, str) is False:
            if len(text) > 40:
                text = text[0:40]

            if isinstance(text, tuple):
                text = tuple([x + ';\n' for x in text])
            else:
                new_text = []

                for item in text:
                    if isinstance(item, (str, unicode)):
                        new_text.append(item + ';\n')
                text = new_text

        return text


class GeolocationFieldRenderer(BaseFieldRenderer):
    """ Geolocation field adapter for excel export"""
    adapts(IGeolocationField, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)

        if not value or value == NO_VALUE:
            return ""

        text = safe_unicode(self._get_text(value))

        location = {'latitude': text.latitude, 'longitude': text.longitude}

        return str(location)


class TupleFieldRenderer(BaseFieldRenderer):
    """ Tuple field adapter for excel export"""
    adapts(ITuple, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)

        if not value or value == NO_VALUE:
            return ""

        text = safe_unicode(self._get_text(value))

        if isinstance(text, str) is False:
            if len(text) > 10:
                text = text[0:10]

            if isinstance(text, tuple):
                text = tuple([x + ';\n' for x in text])
            else:
                counter = 0

                while counter < len(text):
                    text[counter] += ';\n'
                    counter += 1

        return text


class TextLineFieldRenderer(BaseFieldRenderer):
    """ TextLine field adapter for excel export"""
    adapts(ITextLine, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)

        if not value or value == NO_VALUE:
            return ""

        text = safe_unicode(self._get_text(value))

        return text


class PortalTypeRenderer(BaseFieldRenderer):
    """ Portal type adapter for excel export"""
    adapts(PortalType, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """

        return portal.get().portal_types.get(obj.portal_type).title


class AbsoluteUrlRenderer(BaseFieldRenderer):
    """ Absolute url adapter for excel export"""
    adapts(AbsoluteUrl, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """

        return obj.absolute_url()


class UploaderRenderer(BaseFieldRenderer):
    """ Uploader adapter for excel export"""
    adapts(Uploader, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """

        return '; '.join(obj.creators)


class TextFieldRenderer(BaseFieldRenderer):
    """ Text field adapter for excel export"""
    adapts(IText, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)

        if not value or value == NO_VALUE:
            return ""

        text = safe_unicode(self._get_text(value))

        return text


class YearFieldRenderer(BaseFieldRenderer):
    """ Year field adapter for excel export"""

    adapts(Year, Interface, Interface)

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)

        if not value or value == NO_VALUE:
            return ""
        text = safe_unicode(self._get_text(value))

        return str(text)