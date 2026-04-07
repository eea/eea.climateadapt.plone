"""Optimize the storage of image blobs by delegating to the canonical field"""

from plone import api
from plone.api.env import adopt_roles
from plone.api.exc import UserNotFoundError
import logging
import time

from Acquisition import aq_base, aq_parent
from plone.uuid.interfaces import IUUID
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.multilingual.dx.interfaces import IDexterityTranslatable
from plone.dexterity.interfaces import IDexterityContent, IDexterityContainer
from plone.app.multilingual.interfaces import (
    ILanguageRootFolder,
    IMutableTG,
    ITG,
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


def _log_invalid_canonical(context, canonical, caller_name="unknown"):
    """
    Log when an invalid canonical object (e.g. RequestContainer)
    is returned by the translation manager.
    """
    try:
        context_url = context.absolute_url()
    except Exception:
        context_url = f"ERROR getting URL for {repr(context)}"

    try:
        canonical_type = str(type(canonical))
        canonical_repr = repr(canonical)
    except Exception:
        canonical_type = "ERROR getting type"
        canonical_repr = "ERROR getting repr"

    logger.warning(
        f"[{caller_name}] Translation Manager returned invalid canonical object for {context_url}."
        f" Expected object providing IDexterityTranslatable, got {canonical_type}: {canonical_repr}"
    )


def _log_attribute_error_canonical(context, canonical, caller_name="unknown", exc=None):
    """
    Log when a valid canonical object is missing an expected attribute.
    """
    try:
        context_url = context.absolute_url()
    except Exception:
        context_url = f"ERROR getting URL for {repr(context)}"

    try:
        canonical_url = canonical.absolute_url()
    except Exception:
        canonical_url = f"ERROR getting URL for canonical {repr(canonical)}"

    logger.warning(
        f"[{caller_name}] Canonical object missing attribute for {context_url}."
        f" Canonical: {canonical_url} ({type(canonical)}). Error: {exc}"
    )


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

            with adopt_roles(roles=["Owner"]):
                canonical = tm.get_translation("en")
                if canonical is not None:
                    if not (IDexterityTranslatable.providedBy(canonical) and IDexterityContent.providedBy(canonical)):
                        _log_invalid_canonical(
                            self.context, canonical, "LanguageAwareLeadImage.image"
                        )
                        return None
                    try:
                        return canonical.image
                    except AttributeError as e:
                        _log_attribute_error_canonical(
                            self.context, canonical, "LanguageAwareLeadImage.image attribute error", e
                        )
                        return None

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
        canonical = None
        with adopt_roles(roles=["Owner"]):
            canonical = tm.get_translation("en")
            if canonical is None:
                return
            if not (IDexterityTranslatable.providedBy(canonical) and IDexterityContent.providedBy(canonical)):
                _log_invalid_canonical(
                    self.context, canonical, "LanguageAwareImageFieldScales.__call__"
                )
                return

        self.canonical = canonical
        try:
            image = self.field.get(canonical)
        except AttributeError as e:
            _log_attribute_error_canonical(
                self.context, canonical, "LanguageAwareImageFieldScales.__call__ attribute error", e
            )
            return

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
        # logger.info(f"scale url {url}")
        return url


@adapter(INamedImageField, IDexterityTranslatable, IEEAClimateAdaptInstalled)
class LanguageAwareImageFieldSerializer(ImageFieldSerializer):
    def __call__(self):
        lang = ILanguage(self.context).get_language()

        if lang == "en":
            return super().__call__()

        tm = ITranslationManager(self.context)

        canonical = None
        try:
            with adopt_roles(roles=["Owner"]):
                canonical = tm.get_translation("en")
        except UserNotFoundError:
            canonical = tm.get_translation("en")

        if canonical is None:
            return

        if not (IDexterityTranslatable.providedBy(canonical) and IDexterityContent.providedBy(canonical)):
            _log_invalid_canonical(
                self.context, canonical, "LanguageAwareImageFieldSerializer.__call__"
            )
            return

        self.context = canonical
        try:
            return super().__call__()
        except AttributeError as e:
            _log_attribute_error_canonical(
                self.context, canonical, "LanguageAwareImageFieldSerializer.__call__ attribute error", e
            )
            return


@adapter(INamedFileField, IDexterityTranslatable, IEEAClimateAdaptInstalled)
class LanguageAwareFileFieldSerializer(FileFieldSerializer):
    def __call__(self):
        lang = ILanguage(self.context).get_language()

        if lang == "en":
            return super().__call__()

        tm = ITranslationManager(self.context)

        canonical = None
        try:
            with adopt_roles(roles=["Owner"]):
                canonical = tm.get_translation("en")
        except UserNotFoundError:
            canonical = tm.get_translation("en")

        if canonical is None:
            return

        if not (IDexterityTranslatable.providedBy(canonical) and IDexterityContent.providedBy(canonical)):
            _log_invalid_canonical(
                self.context, canonical, "LanguageAwareFileFieldSerializer.__call__"
            )
            return

        self.context = canonical
        try:
            return super().__call__()
        except AttributeError as e:
            _log_attribute_error_canonical(
                self.context, canonical, "LanguageAwareFileFieldSerializer.__call__ attribute error", e
            )
            return


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

        canonical = None
        with adopt_roles(roles=["Owner"]):
            canonical = tm.get_translation("en")
            if canonical is None:
                return False
            if not (IDexterityTranslatable.providedBy(canonical) and IDexterityContent.providedBy(canonical)):
                _log_invalid_canonical(obj, canonical, "hasPreviewImage (indexer)")
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
    with adopt_roles(roles=["Owner"]):
        lang = ILanguage(obj).get_language()
        if lang == "en":
            base_obj = aq_base(obj)
        else:
            tm = ITranslationManager(obj)

            canonical = None
            with adopt_roles(roles=["Owner"]):
                canonical = tm.get_translation("en")
            if canonical is None:
                return image_field
            if not (IDexterityTranslatable.providedBy(canonical) and IDexterityContent.providedBy(canonical)):
                _log_invalid_canonical(obj, canonical, "image_field_indexer")
                return image_field
            base_obj = aq_base(canonical)

        if (
            getattr(base_obj, "preview_image_link", False)
            and not base_obj.preview_image_link.isBroken()
        ):
            image_field = "preview_image_link"
        elif getattr(base_obj, "preview_image", False):
            image_field = "preview_image"
        elif getattr(base_obj, "primary_photo", False):
            image_field = "primary_photo"
        elif getattr(base_obj, "image", False):
            image_field = "image"
    return image_field


class LanguageAwareImageScaling(ImageScaling):
    def __init__(self, context, request, **info):
        lang = ILanguage(context).get_language()
        if lang != "en":
            tm = ITranslationManager(context)

            canonical = None
            with adopt_roles(roles=["Owner"]):
                canonical = tm.get_translation("en")
            if canonical is not None:
                if IDexterityTranslatable.providedBy(canonical) and IDexterityContent.providedBy(canonical):
                    context = canonical
                else:
                    _log_invalid_canonical(
                        context, canonical, "LanguageAwareImageScaling.__init__"
                    )

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
        canonical_type = self.context.portal_type

        if language != "en":
            if content_id in parent.objectIds():
                existing = parent[content_id]

                try:
                    existing_tg = str(ITG(existing))
                    canonical_tg = str(ITG(self.context))
                except TypeError:
                    # Not translatable - delete orphan
                    logger.warning("Deleting non-translatable object at %s", content_id)
                    api.content.delete(obj=existing, check_linkintegrity=False)
                    return content_id

                # Same portal_type
                if existing.portal_type == canonical_type:
                    if existing_tg != canonical_tg:
                        # Fix the TG registration
                        logger.info(
                            "Fixing TG for %s: %s -> %s",
                            content_id,
                            existing_tg,
                            canonical_tg,
                        )
                        IMutableTG(existing).set(canonical_tg)
                        existing.reindexObject(idxs=("TranslationGroup",))
                    # Object already exists with correct (or now fixed) TG
                    raise ValueError(f"Translation already exists: {content_id}")

                # Different portal_type - need to remove/replace
                else:
                    if IDexterityContainer.providedBy(existing) and existing.objectIds():
                        # Folder with children - rename and migrate
                        _migrate_folder_children(parent, existing, content_id, language)
                    else:
                        # Simple object or empty folder - delete
                        logger.warning(
                            "Deleting blocking object %s (type %s, expected %s)",
                            content_id,
                            existing.portal_type,
                            canonical_type,
                        )
                        api.content.delete(obj=existing, check_linkintegrity=False)

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


def _migrate_folder_children(parent, old_folder, target_id, language):
    """
    Handle the case where a folder at the translation target path has children.

    Strategy:
    1. Rename the old folder to a temporary ID (e.g., "events-orphaned-12345")
    2. Create the new translation object (caller will do this)
    3. Queue translation sync for all children to move them to the new folder
    """
    from eea.climateadapt.translation.core import queue_job

    temp_id = f"{target_id}-orphaned-{int(time.time())}"
    logger.warning(
        "Folder %s has children. Renaming to %s and will migrate children.",
        target_id,
        temp_id,
    )

    # Rename old folder
    parent.manage_renameObject(target_id, temp_id)
    old_folder = parent[temp_id]  # Re-fetch after rename

    # Queue path sync jobs for each child in the old folder
    old_folder_path = "/".join(old_folder.getPhysicalPath())
    new_folder_path = "/".join(parent.getPhysicalPath()) + "/" + target_id

    for child_id in old_folder.objectIds():
        data = {
            "newName": child_id,
            "oldName": child_id,
            "oldParent": old_folder_path,
            "newParent": new_folder_path.replace(f"/{language}/", "/en/"),  # Map to EN path
            "expected_uid": IUUID(old_folder[child_id], None),
            "langs": [language],
            "debug_info": {
                "event_trigger": "folder_child_migration",
                "orphaned_folder": temp_id,
            },
        }
        queue_job("sync_paths", "sync_translated_paths", data)
