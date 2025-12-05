from zope.interface import alsoProvides
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from eea.climateadapt import CcaAdminMessageFactory as _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import provider
from zope.schema import Choice


@provider(IFormFieldProvider)
class IRedirectionType(model.Schema):
    """Behavior to add redirection type selection to Link content type"""

    redirection_type = Choice(
        title=_("Type"),
        description=_("Select the HTTP redirection type for this link"),
        vocabulary="eea.climateadapt.redirection_types",
        required=False,
        missing_value=None,
    )


alsoProvides(IRedirectionType["redirection_type"], ILanguageIndependentField)