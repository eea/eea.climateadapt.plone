from plone.app.dexterity.behaviors.nextprevious import INextPreviousToggle
from zope.interface import alsoProvides
from collective.volto.subsites.content.subsite import ISubsite
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.contenttypes.behaviors.tableofcontents import ITableOfContents
# from plone.app.contenttypes.behaviors.leadimage import ILeadImage


alsoProvides(ISubsite["subsite_logo"], ILanguageIndependentField)
alsoProvides(ISubsite["subsite_css_class"], ILanguageIndependentField)
alsoProvides(ISubsite["subsite_social_links"], ILanguageIndependentField)

alsoProvides(ITableOfContents["table_of_contents"], ILanguageIndependentField)
# alsoProvides(ILeadImage["image"], ILanguageIndependentField)

alsoProvides(
    INextPreviousToggle["nextPreviousEnabled"], ILanguageIndependentField)


def apply_patch():
    pass  # nothing, we rely on side-effect
