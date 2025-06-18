from plone.restapi.serializer.dxfields import (
    DefaultFieldSerializer,
    ImageFieldSerializer,
    FileFieldSerializer,
)
from plone.namedfile.interfaces import INamedFileField
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.multilingual.interfaces import ITranslationManager
from plone.base.interfaces import IImageScalesFieldAdapter, ILanguage
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.adapters import ImageFieldScales as BaseImageFieldScales
from plone.namedfile.interfaces import INamedImageField
from zope.component import adapter, getMultiAdapter
from zope.interface import implementer
from zope.interface.interfaces import ComponentLookupError

from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled


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


@implementer(IImageScalesFieldAdapter)
@adapter(INamedImageField, IDexterityContent, IEEAClimateAdaptInstalled)
class LanguageAwareImageFieldScales(BaseImageFieldScales):
    def __call__(self):
        lang = ILanguage(self.context).get_language()

        if lang == "en":
            return super().__call__()

        tm = ITranslationManager(self.context)
        canonical = tm.get_translation("en")
        if canonical is None:
            return

        image = self.field.get(canonical)
        if not image:
            return

        # Get the @@images view once and store it, so all methods can use it.
        try:
            self.images_view = getMultiAdapter((canonical, self.request), name="images")
        except ComponentLookupError:
            # Seen in plone.app.caching.tests.test_profile_with_caching_proxy.
            # If we cannot find the images view, there is nothing for us to do.
            return
        width, height = image.getImageSize()
        url = self.get_original_image_url(self.field.__name__, width, height)
        scales = self.get_scales(self.field, width, height)

        # Return a list with one dictionary.  Why a list?
        # Some people feel a need in custom code to support a different adapter for
        # RelationList fields.  Such a field may point to three images.
        # In that case the adapter could return information for all three images,
        # so a list of three dictionaries.  The default case should use the same
        # structure.
        print("Using canonical", canonical)
        return [
            {
                "filename": image.filename,
                "content-type": image.contentType,
                "size": image.getSize(),
                "download": self._scale_view_from_url(url),
                "width": width,
                "height": height,
                "scales": scales,
            }
        ]


@adapter(INamedImageField, IDexterityContent, IEEAClimateAdaptInstalled)
class LanguageAwareImageFieldSerializer(ImageFieldSerializer):
    def __call__(self):
        lang = ILanguage(self.context).get_language()

        if lang == "en":
            return super().__call__()

        tm = ITranslationManager(self.context)
        canonical = tm.get_translation("en")
        if canonical is None:
            return

        self.context = canonical
        return super().__call__()


@adapter(INamedFileField, IDexterityContent, IEEAClimateAdaptInstalled)
class LanguageAwareFileFieldSerializer(FileFieldSerializer):
    def __call__(self):
        lang = ILanguage(self.context).get_language()

        if lang == "en":
            return super().__call__()

        tm = ITranslationManager(self.context)
        canonical = tm.get_translation("en")
        if canonical is None:
            return

        self.context = canonical
        return super().__call__()
