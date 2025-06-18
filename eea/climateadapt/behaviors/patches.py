from collective.volto.subsites.content.subsite import ISubsite
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.contenttypes.behaviors.tableofcontents import ITableOfContents
from plone.app.dexterity.behaviors.nextprevious import INextPreviousToggle
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.interfaces import ITranslationManager
from plone.base.interfaces import ILanguage
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapter
from zope.interface import alsoProvides, implementer

alsoProvides(ISubsite["subsite_logo"], ILanguageIndependentField)
alsoProvides(ISubsite["subsite_css_class"], ILanguageIndependentField)
alsoProvides(ISubsite["subsite_social_links"], ILanguageIndependentField)

alsoProvides(ITableOfContents["table_of_contents"], ILanguageIndependentField)
alsoProvides(ILeadImageBehavior["image"], ILanguageIndependentField)

alsoProvides(INextPreviousToggle["nextPreviousEnabled"], ILanguageIndependentField)

# ILanguageIndependentFieldsManager,
# ITranslationLocator,
# ITranslationManager,


@implementer(ILeadImageBehavior)
@adapter(IDexterityContent)
class LanguageAwareLeadImage:
    def __init__(self, context):
        self.context = context

    @property
    def image(self):
        lang = ILanguage(self.context).get_language()
        if lang == "en":
            print("en, ")
            return self.context.image
        else:
            tm = ITranslationManager(self.context)
            canonical = tm.get_translation("en")
            if canonical is not None:
                print(f"Returning canonical image for {lang}", canonical.image)
                return canonical.image

    @image.setter
    def image(self, value):
        lang = ILanguage(self.context).get_language()

        if lang != "en":
            print("Setting none for ", lang)
            return
        else:
            print("Setting for english")
            self.context.image = value
            # raise ValueError("Image field should not be set on a translation")

    @property
    def image_caption(self):
        return self.context.image_caption

    @image_caption.setter
    def image_caption(self, value):
        self.context.image_caption = value


def apply_patch():
    pass  # nothing, we rely on side-effect
