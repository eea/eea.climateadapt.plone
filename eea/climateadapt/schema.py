""" zope.schema extensions
"""

from zope.schema import TextLine
from Products.CMFPlone.PloneTool import EMAIL_RE
from zope.schema import ValidationError


class Year(TextLine):
    """ This is actually an Int field, we just don't want what's coming with it

    We do this field to avoid IDataConverter, we want to display simple digits
    with no formatting
    """

    def validate(self, v):
        if not v:
            return
        if v < 1800 or v > 2200:
            raise ValueError (u"Value outside of normal range: 1800-2200")

    def fromUnicode(self, str):
        """
        >>> f = Int()
        >>> f.fromUnicode("125")
        125
        >>> f.fromUnicode("125.6") #doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ValueError: invalid literal for int(): 125.6
        """
        v = int(str)
        self.validate(v)
        return v


class InvalidEmail(ValidationError):
    """ Invalid Email Address """


class Email(TextLine):
    def validate(self, value):
        if value:
            check_value = EMAIL_RE.sub('', value)
            if check_value != '':
                raise InvalidEmail
        return True
