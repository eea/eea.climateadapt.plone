# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
import json
from plone import schema
from zope.interface import Interface
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from eea.climateadapt import CcaAdminMessageFactory as _


class IImageScalesAdapter(Interface):
    """Return a list of image scales for the given context."""

    def __init__(self, context, request):
        """Adapts context and the request."""

    def __call__(self):
        """Call IImageScalesFieldAdapter on all fields."""


class IImageScalesFieldAdapter(Interface):
    """Adapter from field to image_scales.
    This is called by an IImageScalesAdapter.
    Default expectation is that there will be adapters for image fields
    and not for others.  But adapters for text fields or relation fields
    are imaginable.
    """

    def __init__(self, field, context, request):
        """Adapts field, context and request."""

    def __call__(self):
        """Returns JSON compatible python data."""


class IImagingSchema(Interface):
    """
    Schema for Images Controlpanel
    """

    allowed_sizes = schema.List(
        title=_("Allowed image sizes"),
        description=_(
            "Specify all allowed maximum image dimensions, one per line. The "
            "required format is &lt;name&gt; &lt;width&gt;:&lt;height&gt;."
        ),
        value_type=schema.TextLine(),
        default=[
            "huge 1600:65536",
            "great 1200:65536",
            "larger 1000:65536",
            "large 800:65536",
            "teaser 600:65536",
            "preview 400:65536",
            "mini 200:65536",
            "thumb 128:128",
            "tile 64:64",
            "icon 32:32",
            "listing 16:16",
        ],
        missing_value=[],
        required=False,
    )

    quality = schema.Int(
        title=_("Scaled image quality"),
        description=_(
            "A value for the quality of scaled images, from 1 "
            "(lowest) to 95 (highest). A value of 0 will mean "
            "plone.scaling's default will be used, which is "
            "currently 88."
        ),
        min=0,
        max=95,
        default=88,
    )

    highpixeldensity_scales = schema.Choice(
        title=_("High pixel density mode"),
        description=_(""),
        default="disabled",
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm("disabled", "disabled", "Disabled"),
                SimpleTerm("2x", "2x", "Enabled (2x)"),
                SimpleTerm("3x", "3x", "Enabled (2x, 3x)"),
            ]
        ),
    )

    quality_2x = schema.Int(
        title=_("Image quality at 2x"),
        description=_(
            "A value for the quality of 2x high pixel density images, from 1 "
            "(lowest) to 95 (highest). A value of 0 will mean "
            "plone.scaling's default will be used, which is "
            "currently 62."
        ),
        min=0,
        max=95,
        default=62,
    )

    quality_3x = schema.Int(
        title=_("Image quality at 3x"),
        description=_(
            "A value for the quality of 3x high pixel density images, from 1 "
            "(lowest) to 95 (highest). A value of 0 will mean "
            "plone.scaling's default will be used, which is "
            "currently 51."
        ),
        min=0,
        max=95,
        default=51,
    )

    # picture_variants = schema.JSONField(
    #     title=_("Picture variants"),
    #     description=_(
    #         "Enter a JSON-formatted picture variants configuration."
    #     ),
    #     schema=json.dumps(
    #         {
    #             "title": "Image srcset definition",
    #             "type": "object",
    #             "additionalProperties": {"$ref": "#/$defs/srcset"},
    #             "$defs": {
    #                 "srcset": {
    #                     "type": "object",
    #                     "properties": {
    #                         "title": {
    #                             "type": "string",
    #                         },
    #                         "preview": {
    #                             "type": "string",
    #                         },
    #                         "hideInEditor": {
    #                             "type": "boolean",
    #                         },
    #                         "sourceset": {
    #                             "type": "array",
    #                             "items": {
    #                                 "type": "object",
    #                                 "properties": {
    #                                     "scale": {
    #                                         "type": "string",
    #                                     },
    #                                     "media": {
    #                                         "type": "string",
    #                                     },
    #                                     "additionalScales": {
    #                                         "type": "array",
    #                                     },
    #                                 },
    #                                 "additionalProperties": False,
    #                                 "required": ["scale"],
    #                             },
    #                         },
    #                     },
    #                     "additionalProperties": False,
    #                     "required": ["title", "sourceset"],
    #                 },
    #             },
    #         }
    #     ),
    #     default={
    #         "large": {
    #             "title": "Large",
    #             "sourceset": [
    #                 {
    #                     "scale": "larger",
    #                     "additionalScales": [
    #                         "preview",
    #                         "teaser",
    #                         "large",
    #                         "great",
    #                         "huge",
    #                     ],
    #                 },
    #             ],
    #         },
    #         "medium": {
    #             "title": "Medium",
    #             "sourceset": [
    #                 {
    #                     "scale": "teaser",
    #                     "additionalScales": [
    #                         "preview",
    #                         "large",
    #                         "larger",
    #                         "great",
    #                     ],
    #                 },
    #             ],
    #         },
    #         "small": {
    #             "title": "Small",
    #             "sourceset": [
    #                 {
    #                     "scale": "preview",
    #                     "additionalScales": ["large", "larger"],
    #                 },
    #             ],
    #         },
    #     },
    #     required=True,
    # )

    image_captioning = schema.Bool(
        title=_("image_captioning_title", "Enable image captioning"),
        description=_(
            "image_captioning_description",
            "Enable automatic image captioning for images set in the richtext"
            "editor based on the description of images.",
        ),
        default=True,
        required=False,
    )
