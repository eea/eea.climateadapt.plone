from eea.climateadapt import CcaAdminMessageFactory as _
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class ITopLevelVisibility(model.Schema):
    # model.fieldset(
    #     "settings",
    #     label=_("Settings"),
    #     fields=["id"],
    # )

    show_in_top_level = schema.Bool(
        title=_("Show as top level section"),
        description=_("If set on a page in a root, will show that page or "
                      "folder in the global navigation menu"),
        required=False,
    )
    directives.write_permission(show_in_top_level="cmf.ManagePortal")
