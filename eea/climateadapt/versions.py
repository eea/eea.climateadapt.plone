from zope.interface import Interface, Attribute
from zope.annotation import factory

KEY = "SERIAL_ID"


class ISerialId(Interface):
    """change version"""

    serial_id = Attribute("serial_id")


def _serial_factory():
    """Simple serial id factory, return number 0"""

    return 0


change_version_annotation = factory(_serial_factory, key=KEY)
