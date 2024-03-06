from Acquisition import aq_base
from plone.namedfile.scaling import ImageScaling as BaseImageScaling
from zope.publisher.interfaces import IPublishTraverse
from zope.traversing.interfaces import ITraversable
from zope.interface import implementer
from zope.app.file.file import FileChunk


def get_data(value):
    orig_data = None
    try:
        orig_data = value.open().read()
    except AttributeError:
        orig_data = getattr(aq_base(value), "data", value)
    if not orig_data:
        return

    if isinstance(orig_data, FileChunk):
        # Convert data to 8-bit string
        # (FileChunk does not provide read() access)
        orig_data = str(orig_data)

    return orig_data


@implementer(ITraversable, IPublishTraverse)
class ImageScaling(BaseImageScaling):
    def create(
        self, fieldname, direction="thumbnail", height=None, width=None, **parameters
    ):
        orig_value = getattr(self.context, fieldname)
        if orig_value is None:
            return

        if ".svg" in orig_value.filename.lower():
            format_ = "SVG"
            dimensions = (width, height)
            data = get_data(orig_value)

            mimetype = "image/svg+xml"
            value = orig_value.__class__(
                data, contentType=mimetype, filename=orig_value.filename
            )
            return value, format_, dimensions
        else:
            return super(ImageScaling, self).create(
                fieldname, direction, height, width, **parameters
            )
