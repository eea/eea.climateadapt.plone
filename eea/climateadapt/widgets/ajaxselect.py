""" Override AjaxSelectWidget to make better functionality
"""

from html.parser import HTMLParser
from plone.app.widgets.dx import AjaxSelectWidget
from plone.app.widgets.dx import AjaxSelectWidgetConverter as BaseDC
from plone.app.widgets.dx import IAjaxSelectWidget
from zope.component import adapts
from zope.interface import implementsOnly
from zope.schema.interfaces import ICollection


parser = HTMLParser()

class IBetterAjaxSelectWidget(IAjaxSelectWidget):
    """ Marker interface for improved ajax select widget
    """


class BetterAjaxSelectWidget(AjaxSelectWidget):
    """Ajax select widget for z3c.form."""

    implementsOnly(IBetterAjaxSelectWidget)


class BetterAjaxSelectWidgetConverter(BaseDC):
    """Data converter for ICollection fields using the AjaxSelectWidget.
    """

    adapts(ICollection, IBetterAjaxSelectWidget)

    def toFieldValue(self, value):
        """ Rewritten for better behavior.

        Improvements: strip tags, unescape tags, make tags unique

        Converts from widget value to field.

        :param value: Value inserted by AjaxSelect widget.
        :type value: string

        :returns: List of items
        :rtype: list | tuple | set
        """
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        if not len(value):
            return self.field.missing_value
        valueType = self.field.value_type._type
        if isinstance(valueType, tuple):
            valueType = valueType[0]
        separator = getattr(self.widget, 'separator', ';')
        value = parser.unescape(value)
        value = list(set(v.strip() for v in (valueType and valueType(v) or v
            for v in value.split(separator))))
        return collectionType(value)
