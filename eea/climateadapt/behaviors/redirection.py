from zope.interface import alsoProvides
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from eea.climateadapt import CcaAdminMessageFactory as _
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IRedirectionType(model.Schema):
    """Behavior to add redirection type selection to Link content type"""

    redirection_type = schema.Choice(
        title=_("Redirection type"),
        description=_("Select the HTTP redirection type for this link"),
        vocabulary="eea.climateadapt.redirection_types",
        default="302",
        required=False,
    )


alsoProvides(IRedirectionType["redirection_type"], ILanguageIndependentField)