from zope.schema import Bool
from plone.supermodel import model
from zope.interface import provider
from plone.autoform.interfaces import IFormFieldProvider

@provider(IFormFieldProvider)
class INonstructuralSection(model.Schema):
    is_nonstructural_folder = Bool(
        title="Non-clickable in main menu",
        description="When enabled, this folder will not be clickable in the main menu",
        required=False,
        missing_value=False
    )
