from zope.interface import Interface, Attribute, implementer
from zope.annotation import factory
from zope.component import adapter
from plone.dexterity.interfaces import IDexterityContent

KEY = "SERIAL_ID"


class ISerialId(Interface):
    """change version"""

    serial_id = Attribute("serial_id")


@adapter(IDexterityContent)
@implementer(ISerialId)
def _serial_factory():
    """Simple serial id factory, return number 0"""

    return 0


change_version_annotation = factory(_serial_factory, key=KEY)
