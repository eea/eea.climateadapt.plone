from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import provider

from eea.climateadapt import CcaAdminMessageFactory as _


@provider(IFormFieldProvider)
class ISEOFields(model.Schema):
    """ """

    model.fieldset(
        "seofields",
        label=_("SEO"),
        fields=("seo_noindex",),
    )

    # based on https://github.com/kitconcept/kitconcept.seo/blob/main/src/kitconcept/seo/behaviors/seo.py
    # https://support.google.com/webmasters/answer/93710?hl=en
    seo_noindex = schema.Bool(
        title=_("No Index"),
        description=_("Prevents a page from appearing in search engines"),
        required=False,
    )
