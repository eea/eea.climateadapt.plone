from collective.volto.subsites.content.subsite import ISubsite
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.contenttypes.behaviors.tableofcontents import ITableOfContents
from plone.app.dexterity.behaviors.nextprevious import INextPreviousToggle
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from zope.interface import alsoProvides

alsoProvides(ISubsite["subsite_logo"], ILanguageIndependentField)
alsoProvides(ISubsite["subsite_css_class"], ILanguageIndependentField)
alsoProvides(ISubsite["subsite_social_links"], ILanguageIndependentField)

alsoProvides(ITableOfContents["table_of_contents"], ILanguageIndependentField)
alsoProvides(ILeadImageBehavior["image"], ILanguageIndependentField)

alsoProvides(INextPreviousToggle["nextPreviousEnabled"], ILanguageIndependentField)

# ILanguageIndependentFieldsManager,
# ITranslationLocator,
# ITranslationManager,


def apply_patch():
    pass  # nothing, we rely on side-effect
