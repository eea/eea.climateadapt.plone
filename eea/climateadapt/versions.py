from zope.interface import Interface, Attribute, implementer
from zope.annotation import factory
from zope.component import adapter
from plone.dexterity.interfaces import IDexterityContent
from zope.annotation.interfaces import IAnnotations
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

KEY = "SERIAL_ID"


class ISerialId(Interface):
    """change version"""

    serial_id = Attribute("serial_id")


@adapter(IDexterityContent)
@implementer(ISerialId)
def _serial_factory(context):
    """Simple serial id factory, return number 0"""
    return IAnnotations(context).get(KEY, 0)


change_version_annotation = factory(_serial_factory, key=KEY)


def increment_serial_id(obj, event):
    annotations = IAnnotations(obj)
    val = annotations.get(KEY, 0)
    annotations[KEY] = val + 1
    # logger.info("Incremented serial_id for %s to %s", obj.absolute_url(), val + 1)
