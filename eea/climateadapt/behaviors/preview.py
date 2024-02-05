# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope.interface import provider
from zope.schema import TextLine


@provider(IFormFieldProvider)
class IPreview(model.Schema):

    preview_image = namedfile.NamedBlobImage(
        title=(u"Preview image"),
        description=(u"Insert an image that will be used in listing and teaser blocks."),
        required=False,
    )

    preview_caption = TextLine(
        title=(u"Preview image caption"), description=(u""), required=False
    )