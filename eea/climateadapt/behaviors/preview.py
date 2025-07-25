# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope.interface import provider
from zope.schema import TextLine


@provider(IFormFieldProvider)
class IPreview(model.Schema):
    preview_image = namedfile.NamedBlobImage(
        title=("Preview image"),
        description=("Insert an image that will be used in listing and teaser blocks."),
        required=False,
    )

    preview_caption = TextLine(
        title=("Preview image caption"), description=(""), required=False
    )


# blobs are handled by field serializer
# from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
# from zope.interface import alsoProvides
# alsoProvides(IPreview["preview_image"], ILanguageIndependentField)
