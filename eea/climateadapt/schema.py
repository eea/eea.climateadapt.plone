""" zope.schema extensions
"""

from zope.schema import TextLine


class Year(TextLine):
    """ This is actually an Int field, we just don't want what's coming with it

    We do this field to avoid IDataConverter, we want to display simple digits
    with no formatting
    """

    def validate(self, v):
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
