# from collective.excelexport.exportables.base import BaseExportableFactory
# from collective.excelexport.exportables.dexterityfields import \
#     BaseFieldRenderer
from zope.component import adapts
from zope.interface import Interface
from zope.schema.interfaces import IDatetime, IList, IText, ITextLine, ITuple

from eea.climateadapt.schema import AbsoluteUrl, PortalType, Uploader, Year
from plone.app.textfield.interfaces import IRichText
from plone.api import content, portal
from plone.dexterity.interfaces import IDexterityFTI
# from plone.formwidget.geolocation.interfaces import IGeolocationField
from Products.CMFPlone.utils import safe_unicode
from z3c.form.interfaces import NO_VALUE
from z3c.relationfield.interfaces import IRelationList
from collective.excelexport.view import BaseExport

from io import StringIO  ## for Python 3
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from collective.excelexport.interfaces import IStyles
import xlwt
from xlwt import CompoundDoc
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from copy import copy
from DateTime import DateTime
import datetime

class ExcelExport(BaseExport):
    """Excel export view
    """

    mimetype = "application/vnd.ms-excel"
    extension = "xls"
    encoding = "windows-1252"

    def _format_render(self, render):
        """Common formatting to unicode
        """
        if isinstance(render, Message):
            render = translate(render, context=self.request)
        elif isinstance(render, str):
            pass
        elif render is None:
            render = ""
        elif isinstance(render, str):
            render = safe_unicode(render)
        elif isinstance(render, datetime.datetime):
            render = safe_unicode(render.strftime("%Y/%m/%d %H:%M"))
        elif isinstance(render, (DateTime, datetime.date)):
            try:
                render = safe_unicode(render.strftime("%Y/%m/%d"))
            except ValueError:
                # when date < 1900
                render = safe_unicode(render)
        elif not isinstance(render, str):
            render = safe_unicode(str(render))

        return render

    def write_sheet(self, sheet, sheetinfo, styles):
        # values
        for rownum, obj in enumerate(sheetinfo["objects"]):
            _exportablenum = 0
            for exportablenum, exportable in enumerate(sheetinfo["exportables"]):
                try:
                    # dexterity
                    bound_obj = exportable.field.bind(obj).context
                except AttributeError:
                    bound_obj = obj

                # check if is field is block
                render = exportable.render_header()
                render = self._format_render(render)
                if render not in ['Blocks', 'Blocks Layout']:
                    style = exportable.render_style(bound_obj, copy(styles.content))
                    style_headers = getattr(style, "headers", styles.headers)
                    style_content = getattr(style, "content", style)
                    if rownum == 0:
                        # headers
                        render = exportable.render_header()
                        render = self._format_render(render)
                        sheet.write(0, _exportablenum, render, style_headers)

                    render = exportable.render_value(bound_obj)
                    render = self._format_render(render)
                    render = render[0:32766]
                    sheet.write(rownum + 1, _exportablenum, render, style_content)
                    _exportablenum += 1

    def get_xldoc(self, sheetsinfo, styles):
        xldoc = xlwt.Workbook(encoding="utf-8")
        empty_doc = True
        for sheetnum, sheetinfo in enumerate(sheetsinfo):
            if len(sheetinfo["exportables"]) == 0:
                continue

            # sheet
            empty_doc = False
            title = self._format_render(sheetinfo["title"])
            sheet_title = (
                title.replace("'", " ").replace(":", "-").replace("/", "-")[:31]
            )

            try:
                sheet = xldoc.add_sheet(sheet_title)
            except Exception:
                sheet = xldoc.add_sheet(sheet_title + " " + str(sheetnum))

            self.write_sheet(sheet, sheetinfo, styles)

        if empty_doc:
            # empty doc
            sheet = xldoc.add_sheet("sheet 1")
            sheet.write(0, 0, "", styles.content)

        return xldoc

    def get_data_buffer(self, sheetsinfo, policy=""):
        string_buffer = StringIO()
        try:
            styles = getMultiAdapter(
                (self.context, self.request), interface=IStyles, name=policy
            )
        except ComponentLookupError:
            styles = getMultiAdapter((self.context, self.request), interface=IStyles)

        xldoc = self.get_xldoc(sheetsinfo, styles)
        doc = CompoundDoc.XlsDoc()
        data = xldoc.get_biff_data()
        doc.save(string_buffer, data)
        return string_buffer


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


# class MetadataExportablesFactory(BaseExportableFactory):
#     """Get fields content schema
#     """
#     adapts(IDexterityFTI, Interface, Interface)
#     weight = 100

#     def get_exportables(self):
#         exportables = [
#             ObjectStateRenderer(),
#             CreatorRenderer()
#         ]

#         return exportables


# class DateTimeFieldRenderer(BaseFieldRenderer):
#     """ Datetime field adapter for excel export"""
#     adapts(IDatetime, Interface, Interface)

#     def _get_text(self, value):
#         return portal.get_localized_time(datetime=value)

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """
#         value = self.get_value(obj)

#         if not value or value == NO_VALUE:
#             return ""

#         text = safe_unicode(self._get_text(value))

#         return text


# class RelationListFieldRenderer(BaseFieldRenderer):
#     """ Renderer for related items """
#     adapts(IRelationList, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """ Gets the value to render in excel file from content value
#         """

#         value = self.get_value(obj)

#         if not value or value == NO_VALUE:
#             return ""

#         text = safe_unicode(self._get_text(value))

#         new_text = []

#         for item in text:
#             if item.to_object is not None:
#                 new_text.append(item.to_object.Title() + ';\n')
#             else:
#                 pass

#         return new_text


# class ListFieldRenderer(BaseFieldRenderer):
#     """ List field adapter for excel export"""
#     adapts(IList, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """
#         value = self.get_value(obj)

#         if not value or value == NO_VALUE:
#             return ""

#         text = safe_unicode(self._get_text(value))

#         if isinstance(text, str) is False:
#             if len(text) > 40:
#                 text = text[0:40]

#             if isinstance(text, tuple):
#                 text = tuple([x + ';\n' for x in text])
#             else:
#                 new_text = []

#                 for item in text:
#                     if isinstance(item, str):
#                         new_text.append(item + ';\n')
#                 text = new_text

#         return text

# class GeolocationFieldRenderer(BaseFieldRenderer):
#     """ Geolocation field adapter for excel export"""
#     adapts(IGeolocationField, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """
#         value = self.get_value(obj)

#         if not value or value == NO_VALUE:
#             return ""

#         text = safe_unicode(self._get_text(value))

#         location = {'latitude': text.latitude, 'longitude': text.longitude}

#         return str(location)


# class TupleFieldRenderer(BaseFieldRenderer):
#     """ Tuple field adapter for excel export"""
#     adapts(ITuple, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """
#         value = self.get_value(obj)

#         if not value or value == NO_VALUE:
#             return ""

#         text = safe_unicode(self._get_text(value))

#         if isinstance(text, str) is False:
#             if len(text) > 10:
#                 text = text[0:10]

#             if isinstance(text, tuple):
#                 text = tuple([x + ';\n' for x in text])
#             else:
#                 counter = 0

#                 while counter < len(text):
#                     text[counter] += ';\n'
#                     counter += 1

#         return text


# class TextLineFieldRenderer(BaseFieldRenderer):
#     """ TextLine field adapter for excel export"""
#     adapts(ITextLine, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """
#         value = self.get_value(obj)

#         if not value or value == NO_VALUE:
#             return ""

#         text = safe_unicode(self._get_text(value))

#         return text


# class PortalTypeRenderer(BaseFieldRenderer):
#     """ Portal type adapter for excel export"""
#     adapts(PortalType, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """

#         return portal.get().portal_types.get(obj.portal_type).title


# class AbsoluteUrlRenderer(BaseFieldRenderer):
#     """ Absolute url adapter for excel export"""
#     adapts(AbsoluteUrl, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """

#         return obj.absolute_url()


# class UploaderRenderer(BaseFieldRenderer):
#     """ Uploader adapter for excel export"""
#     adapts(Uploader, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """

#         return '; '.join(obj.creators)


# class TextFieldRenderer(BaseFieldRenderer):
#     """ Text field adapter for excel export"""
#     adapts(IText, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """
#         value = self.get_value(obj)

#         if not value or value == NO_VALUE:
#             return ""

#         text = safe_unicode(self._get_text(value))

#         return text


# class RichTextFieldRenderer(BaseFieldRenderer):
#     """ RichText field adapter for excel export"""
#     adapts(IRichText, Interface, Interface)

#     def _get_text(self, value):
#         try:
#             v = value.output
#         except:
#             v = value
            
#         return v

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """
#         value = self.get_value(obj)

#         if not value or value == NO_VALUE:
#             return ""

#         text = safe_unicode(self._get_text(value))

#         return text


# class YearFieldRenderer(BaseFieldRenderer):
#     """ Year field adapter for excel export"""

#     adapts(Year, Interface, Interface)

#     def _get_text(self, value):
#         return value

#     def render_value(self, obj):
#         """Gets the value to render in excel file from content value
#         """
#         value = self.get_value(obj)

#         if not value or value == NO_VALUE:
#             return ""
#         text = safe_unicode(self._get_text(value))

#         return str(text)