from persistent import Persistent
from zope.interface import Interface, Attribute, implementer
from zope.component import adapter
from plone.dexterity.interfaces import IDexterityContent
from zope.annotation.interfaces import IAnnotations
import logging

logger = logging.getLogger("eea.climateadapt")

KEY = "SERIAL_ID"


class ISerialId(Interface):
    """change version"""

    serial_id = Attribute("serial_id")


@adapter(IDexterityContent)
@implementer(ISerialId)
class SerialIdAdapter(Persistent):
    """Simple serial id factory, return number 0"""

    def __init__(self, context):
        self.context = context

    @property
    def serial_id(self):
        """Getter: Retrieve the value from annotations"""
        annotations = IAnnotations(self.context)
        # Return None if the key doesn't exist yet
        return annotations.get(KEY, 0)

    @serial_id.setter
    def serial_id(self, value):
        """Setter: Store the value in annotations"""
        annotations = IAnnotations(self.context)
        annotations[KEY] = value
        annotations[KEY]._p_changed = 1


def increment_serial_id(obj, event):
    sd = ISerialId(obj)
    sd.serial_id += 1
    logger.info("Incremented serial_id for %s to %s", obj.absolute_url(), sd.serial_id)
