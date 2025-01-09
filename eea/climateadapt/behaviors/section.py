from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import alsoProvides, provider
from zope.schema import Bool


@provider(IFormFieldProvider)
class INonstructuralSection(model.Schema):
    is_nonstructural_folder = Bool(
        title=str("Non-clickable in main menu"),
        description=str(
            "When enabled, this folder will not be clickable in the main menu"
        ),
        required=False,
        missing_value=False,
    )


alsoProvides(
    INonstructuralSection["is_nonstructural_folder"], ILanguageIndependentField
)
