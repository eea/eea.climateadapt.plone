"""Optimize the storage of image blobs by delegating to the canonical field"""

from plone.api.env import adopt_user
import logging

from Acquisition import aq_base, aq_parent
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.multilingual.dx.interfaces import IDexterityTranslatable
from plone.app.multilingual.interfaces import (
    ILanguageRootFolder,
    ITranslationCloner,
    ITranslationFactory,
    ITranslationIdChooser,
    ITranslationLocator,
    ITranslationManager,
)
from plone.base.interfaces import IImageScalesFieldAdapter, ILanguage, IPloneSiteRoot
from plone.indexer.decorator import indexer
from plone.namedfile.adapters import ImageFieldScales as BaseImageFieldScales
from plone.namedfile.interfaces import INamedFileField, INamedImageField
from plone.namedfile.scaling import ImageScaling
from plone.restapi.serializer.dxfields import (
    FileFieldSerializer,
    ImageFieldSerializer,
)
from plone.volto.behaviors.preview import IPreview
from zope.component import adapter, getMultiAdapter
from zope.interface import implementer
from zope.interface.interfaces import ComponentLookupError

from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled

logger = logging.getLogger("eea.climateadapt")


@implementer(ILeadImageBehavior)
@adapter(IDexterityTranslatable)
class LanguageAwareLeadImage:
    def __init__(self, context):
        self.context = context

    @property
    def image(self):
        lang = ILanguage(self.context).get_language()
        if lang == "en":
            return self.context.image
        else:
            tm = ITranslationManager(self.context)

            with adopt_user(username="admin"):
                canonical = tm.get_translation("en")
                if canonical is not None:
                    return canonical.image

    @image.setter
    def image(self, value):
        lang = ILanguage(self.context).get_language()

        if lang != "en":
            return
        else:
            self.context.image = value

    @property
    def image_caption(self):
        return self.context.image_caption

    @image_caption.setter
    def image_caption(self, value):
        self.context.image_caption = value


@implementer(IImageScalesFieldAdapter)
@adapter(INamedImageField, IDexterityTranslatable, IEEAClimateAdaptInstalled)
class LanguageAwareImageFieldScales(BaseImageFieldScales):
    canonical = None

    def __call__(self):
        lang = ILanguage(self.context).get_language()

        if lang == "en":
            return super().__call__()

        tm = ITranslationManager(self.context)
        canonical = tm.get_translation("en")
        if canonical is None:
            return

        self.canonical = canonical
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

    def _scale_view_from_url(self, url):
        # The "download" information for scales is the path to
        # "@@images/foo-scale" only.
        # The full URL to the scale is rendered by the scaling adapter at
        # runtime to make sure they are correct in virtual hostings.
        if self.canonical is not None:
            obj = self.canonical
        else:
            obj = self.context
        url = url.replace(obj.absolute_url(), "").lstrip("/")
        logger.info(f"scale url {url}")
        return url


@adapter(INamedImageField, IDexterityTranslatable, IEEAClimateAdaptInstalled)
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


@adapter(INamedFileField, IDexterityTranslatable, IEEAClimateAdaptInstalled)
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


@indexer(IPreview)
def hasPreviewImage(obj):
    """
    Indexer for knowing in a catalog search if a content with the IPreview behavior has
    a preview_image
    """

    lang = ILanguage(obj).get_language()

    if lang == "en":
        base_obj = aq_base(obj)
    else:
        tm = ITranslationManager(obj)
        canonical = tm.get_translation("en")
        if canonical is None:
            return False
        base_obj = aq_base(canonical)

    if base_obj.preview_image or (
        base_obj.preview_image_link and not base_obj.preview_image_link.isBroken()
    ):
        return True
    return False


@indexer(IDexterityTranslatable)
def image_field_indexer(obj):
    """Indexer for knowing in a catalog search if a content has any image."""

    image_field = ""

    # we need adopt_user because indexer is executed at end of the transaction
    # and we use a fake authentication in the @@save-translation page
    with adopt_user(username="admin"):
        lang = ILanguage(obj).get_language()
        if lang == "en":
            base_obj = aq_base(obj)
        else:
            tm = ITranslationManager(obj)
            canonical = tm.get_translation("en")
            if canonical is None:
                return image_field
            base_obj = aq_base(canonical)

        if (
            getattr(base_obj, "preview_image_link", False)
            and not base_obj.preview_image_link.isBroken()
        ):
            image_field = "preview_image_link"
        elif getattr(base_obj, "preview_image", False):
            image_field = "preview_image"
        elif getattr(base_obj, "image", False):
            image_field = "image"
    return image_field


class LanguageAwareImageScaling(ImageScaling):
    def __init__(self, context, request, **info):
        lang = ILanguage(context).get_language()
        if lang != "en":
            tm = ITranslationManager(context)
            canonical = tm.get_translation("en")
            if canonical is not None:
                context = canonical

        self.context = context
        self.request = request


@implementer(ITranslationLocator)
class OverrideDefaultTranslationLocator:
    def __init__(self, context):
        self.context = context

    def __call__(self, language):
        """
        Look for the closest translated folder or siteroot
        """
        parent = aq_parent(self.context)
        translated_parent = parent
        found = False
        while (
            not (
                IPloneSiteRoot.providedBy(parent)
                and not ILanguageRootFolder.providedBy(parent)
            )
            and not found
        ):
            parent_translation = ITranslationManager(parent)
            if parent_translation.has_translation(language):
                translated_parent = parent_translation.get_translation(language)
                found = True
            else:
                raise ValueError("Could not find translated parent")
        return translated_parent


@implementer(ITranslationIdChooser)
class OverrideDefaultTranslationIdChooser:
    def __init__(self, context):
        self.context = context

    def __call__(self, parent, language):
        content_id = self.context.getId()
        if language != "en":
            if content_id in parent.objectIds():
                raise ValueError(
                    f"Translation object already exists, can't be reused {content_id}"
                )
            return content_id
        parts = content_id.split("-")
        # ugly heuristic (searching for something like 'de', 'en' etc.)
        if len(parts) > 1 and len(parts[-1]) == 2:
            content_id = "-".join(parts[:-1])
        while content_id in parent.objectIds():
            content_id = f"{content_id}-{language}"
        return content_id


@implementer(ITranslationFactory)
class OverrideDefaultTranslationFactory:
    def __init__(self, context):
        self.context = context

    def __call__(self, language):
        content_type = self.context.portal_type
        # parent for translation
        locator = ITranslationLocator(self.context)
        parent = locator(language)
        # id for translation
        name_chooser = ITranslationIdChooser(self.context)
        content_id = name_chooser(parent, language)
        # creating the translation
        new_id = parent.invokeFactory(
            type_name=content_type, id=content_id, language=language
        )
        new_content = getattr(parent, new_id)
        # clone language-independent content
        cloner = ITranslationCloner(self.context)
        cloner(new_content)
        return new_content
