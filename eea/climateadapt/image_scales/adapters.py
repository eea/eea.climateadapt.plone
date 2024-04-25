# pylint: disable=ungrouped-imports
"""
ImageScales
"""

import logging

from Acquisition import aq_inner
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.namedfile.interfaces import INamedImageField
from plone.registry.interfaces import IRegistry
from ZODB.POSException import POSKeyError
from zope.component import adapter, getMultiAdapter, getUtility, queryMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, implementer
from zope.schema import getFields

from eea.climateadapt.image_scales.interfaces import (
    IImageScalesAdapter,
    IImageScalesFieldAdapter,
    IImagingSchema,
)

logger = logging.getLogger("eea.climateadapt")


@implementer(IImageScalesAdapter)
@adapter(IDexterityContent, Interface)
class ImageScales(object):
    """
    Adapter for getting image scales
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = aq_inner(self.context)
        res = {}
        for schema in iterSchemata(self.context):
            for name, field in getFields(schema).items():
                # serialize the field
                serializer = queryMultiAdapter(
                    (field, obj, self.request), IImageScalesFieldAdapter
                )
                if serializer:
                    try:
                        scales = serializer()
                        if scales:
                            res[name] = scales
                    except POSKeyError:
                        logger.error("No blobs for %s",
                                     self.context.absolute_url())

        return res


def _split_scale_info(allowed_size):
    """
    get desired attr(name,width,height) from scale names
    """
    name, dims = allowed_size.split(" ")
    width, height = list(map(int, dims.split(":")))
    return name, width, height


def _get_scale_infos():
    """Returns list of (name, width, height) of the available image scales."""
    # __import__("pdb").set_trace()
    if IImagingSchema is None:
        return []
    registry = getUtility(IRegistry)
    imaging_settings = registry.forInterface(
        IImagingSchema, prefix="plone", omit=("picture_variants")
    )
    allowed_sizes = imaging_settings.allowed_sizes
    return [_split_scale_info(size) for size in allowed_sizes]


@implementer(IImageScalesFieldAdapter)
@adapter(INamedImageField, IDexterityContent, Interface)
class ImageFieldScales(object):
    """
    Image scale serializer
    """

    def __init__(self, field, context, request):
        self.context = context
        self.request = request
        self.field = field

    def __call__(self):
        # __import__("pdb").set_trace()
        image = self.field.get(self.context)
        if not image:
            return None

        # Get the @@images view once and store it, so all methods can use it.
        try:
            self.images_view = getMultiAdapter(
                (self.context, self.request), name="images"
            )
        except ComponentLookupError:
            # Seen in plone.app.caching.tests.test_profile_with_caching_proxy.
            # If we cannot find the images view, there is nothing for us to do.
            return None
        # __import__("pdb").set_trace()
        width, height = image.getImageSize()
        url = self.get_original_image_url(self.field.__name__, width, height)

        if url and ".svg" in url:
            bits = url.split("@@images")
            url = bits[0] + "@@download" + "/" + self.field.__name__

        scales = self.get_scales(self.field, width, height)

        return [
            {
                "filename": image.filename,
                "content-type": image.contentType,
                "size": image.getSize(),
                "download": "@@images/%s" % (self.field.__name__),
                # self._scale_view_from_url(url),
                "width": width,
                "height": height,
                "scales": scales,
            }
        ]

    def _get_scale_from_storage(self, fieldname, width, height):
        annot = getattr(self.context, "__annotations__", None)
        if annot is None:
            return None
        storage = annot.get("plone.scale", None)
        if storage is None:
            return None
        # TODO: use an algorithm to detect change of modified image
        for scale in storage.values():
            if scale["fieldname"] == fieldname and (
                scale["width"] == width or scale["height"] == height
            ):
                # TODO: ^^ scaling is weird, we're being extra-permisive here
                return scale

    def get_scales(self, field, width, height):
        """Get a dictionary of available scales for a particular image field,
        with the actual dimensions(aspect ratio of the original image).
        """
        scales = {}

        scale_infos = _get_scale_infos()
        for name, actual_width, actual_height in scale_infos:
            # print(
            #     "eea.climateadapt.image_scales looking up scale",
            #     name,
            #     actual_width,
            #     actual_height,
            #     width,
            # )
            # ('eea.climateadapt.image_scales looking up scale', u'huge', 1600, 65536, 1734)
            # if actual_width > width:
            #     # The width of the scale is larger than the original width.
            #     # Scaling would simply return the original (or perhaps a copy
            #     # with the same size).  We do not need this scale.
            #     # If we *do* want this, we should call the scale method with
            #     # mode="cover", so it scales up.
            #     print("actual width bigger then width", actual_width, width)
            #     continue

            # Get the scale info without actually generating the scale,
            # nor any old-style HiDPI scales.
            try:
                # TODO: try to retrieve the scale from annotation storage
                # current code will always write a scale here
                scale = self._get_scale_from_storage(
                    field.__name__, width=actual_width, height=actual_height
                )
                if scale is None:
                    # __import__("pdb").set_trace()
                    scale = self.images_view.scale(
                        field.__name__,
                        width=actual_width,
                        height=actual_height,
                    )
            except:  # TODO: hotfix for migration
                scale = None
            if scale is None:
                # If we cannot get a scale, it is probably a corrupt image.
                continue

            # __import__("pdb").set_trace()
            if isinstance(scale, dict):
                ext = scale["mimetype"].split("/")[1]
                url = "@@images/%s.%s" % (scale["uid"], ext)

                actual_width = scale["width"]
                actual_height = scale["height"]
            else:
                url = scale.url
                actual_width = scale.width
                actual_height = scale.height

            scales[name] = {
                "download": "@@images/%s/%s" % (field.__name__, name),
                # self._scale_view_from_url(url),
                "width": actual_width,
                "height": actual_height,
            }

        return scales

    def get_original_image_url(self, fieldname, width, height):
        """
        get image url from scale
        """
        try:
            # TODO: temporary hotfix for migration
            scale = self.images_view.scale(
                fieldname,
                width=width,
                height=height,
            )
        except:
            return ""
        # Corrupt images may not have a scale.
        return scale.url if scale else None

    def _scale_view_from_url(self, url):
        """
        flatten to scale url
        """
        # The "download" information for scales is the path to
        # "@@images/foo-scale" only.
        # The full URL to the scale is rendered by the scaling adapter at
        # runtime to make sure they are correct in virtual hostings.
        return url.replace(self.context.absolute_url(), "").lstrip("/")
