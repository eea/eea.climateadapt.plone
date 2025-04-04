# copy and adapted for plone4 from https://github.com/plone/plone.restapi/blob/7833026a16b0c9a4bfb7230dece8c531e9a02eff/src/plone/restapi/services/multilingual/pam.py

from plone.app.multilingual.interfaces import ITranslationLocator
import transaction
import plone.protect.interfaces

from Acquisition import aq_inner
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from zope.component import adapter
from Products.CMFCore.utils import getToolByName
from plone.restapi.services import Service
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.deserializer import json_body
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

# from plone.restapi.bbb import ILanguage
# from plone.restapi.bbb import IPloneSiteRoot


def get_language(obj):
    # replacement for ILanguage(self.context).get_language():
    obj = aq_inner(obj)
    # we fallback to en, not sure if the best
    lang = getattr(obj, "language", "en")
    return lang


@implementer(IExpandableElement)
@adapter(ITranslatable, Interface)
class Translations:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        # __import__("pdb").set_trace()
        result = {
            "translations": {"@id": "%s/@translations" % self.context.absolute_url()}
        }
        if not expand:
            return result

        translations = []
        manager = ITranslationManager(self.context)
        for language, translation in list(manager.get_restricted_translations().items()):
            if language != get_language(self.context):
                translations.append(
                    {"@id": translation.absolute_url(), "language": language}
                )

        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        current_lang_nav_root = portal_state.navigation_root()

        if IPloneSiteRoot.providedBy(current_lang_nav_root):
            # We are not inside a LRF, bail off
            return result

        nav_root_manager = ITranslationManager(current_lang_nav_root)
        nav_root_translations = {}
        for (
            language,
            translation,
        ) in list(nav_root_manager.get_restricted_translations().items()):
            nav_root_translations[language] = translation.absolute_url()

        result["translations"]["items"] = translations
        result["translations"]["root"] = nav_root_translations
        return result


class TranslationInfo(Service):
    """Get translation information"""

    def reply(self):
        translations = Translations(self.context, self.request)
        return translations(expand=True)["translations"]


class LinkTranslations(Service):
    """Link two content objects as translations of each other"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        self.portal_url = self.portal.absolute_url()
        self.catalog = getToolByName(self.context, "portal_catalog")

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request, plone.protect.interfaces.IDisableCSRFProtection)

        data = json_body(self.request)
        id_ = data.get("id", None)
        if id_ is None:
            self.request.response.setStatus(400)
            return dict(
                error=dict(type="BadRequest",
                           message="Missing content id to link to")
            )

        target = self.get_object(id_)
        if target is None:
            self.request.response.setStatus(400)
            return dict(error=dict(type="BadRequest", message="Content does not exist"))
        elif target.portal_type == "LRF":
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest",
                    message="Language Root Folders can only be linked between each other",
                )
            )

        # ILanguage(target).get_language()
        target_language = get_language(target)
        manager = ITranslationManager(self.context)
        current_translation = manager.get_translation(target_language)
        target_manager = ITranslationManager(target)
        target_translation = target_manager.get_translation(
            self.context.language)
        if current_translation is not None:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest",
                    message="Source already translated into language {}".format(
                        target_language
                    ),
                )
            )
        if target_translation is not None:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest",
                    message="Target already translated into language {}".format(
                        target_language
                    ),
                )
            )

        manager.register_translation(target_language, target)
        # We want to leave a log in the transaction that the link has been executed
        ts = transaction.get()
        ts.note(
            "Linked translation %s (%s) -> %s (%s)"
            % (
                "/".join(self.context.getPhysicalPath()),
                self.context.language,
                "/".join(target.getPhysicalPath()),
                target_language,
            )
        )

        self.request.response.setStatus(201)
        self.request.response.setHeader(
            "Location", self.context.absolute_url())
        return {}

    def get_object(self, key):
        if key.startswith(self.portal_url):
            # Resolve by URL
            key = key[len(self.portal_url) + 1:]
            return self.portal.restrictedTraverse(key, None)
        elif key.startswith("/"):
            # Resolve by path
            return self.portal.restrictedTraverse(key.lstrip("/"), None)
        else:
            # Resolve by UID
            brain = self.catalog(UID=key)
            if brain:
                return brain[0].getObject()


class UnlinkTranslations(Service):
    """Unlink the translations for a content object"""

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request, plone.protect.interfaces.IDisableCSRFProtection)

        data = json_body(self.request)
        manager = ITranslationManager(self.context)
        language = data.get("language", None)
        if language is None:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest",
                    message="You need to provide the language to unlink",
                )
            )
        elif language not in list(manager.get_translations()):
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest",
                    message="This objects is not translated into %s" % language,
                )
            )
        elif self.context.portal_type == "LRF":
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest",
                    message="Language Root Folders cannot be unlinked",
                )
            )

        manager.remove_translation(language)
        # We want to leave a log in the transaction that the unlink has been executed
        ts = transaction.get()
        ts.note(
            "Unlinked translation for %s in %s (%s)"
            % (
                language,
                "/".join(self.context.getPhysicalPath()),
                self.context.language,
            )
        )

        return self.reply_no_content()


class TranslationLocator(Service):
    """Get translation locator placements information"""

    def reply(self):
        target_language = self.request.form["target_language"]

        locator = ITranslationLocator(self.context)
        parent = locator(target_language)

        return {"@id": parent.absolute_url()}
