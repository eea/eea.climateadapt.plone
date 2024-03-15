"""Admin translation"""

from eea.climateadapt import CcaAdminMessageFactory as _
from Products.CMFCore.utils import getToolByName
import transaction
from eea.climateadapt.translation.utils import (
    get_site_languages,
)
from Products.CMFPlone import utils
from plone import api
from .core import (
    admin_some_translated,
    copy_missing_interfaces,
    create_translation_object,
    fix_urls_for_translated_content,
    translate_obj,
    translation_list_type_fields,
    translation_step_4,
    translations_status,
    translations_status_by_version,
)
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.globalrequest import getRequest
from zope.site.hooks import getSite
from plone.app.multilingual.manager import TranslationManager

import logging

logger = logging.getLogger("eea.climateadapt")


class TranslationListTypeFields(BrowserView):
    """Use this view to translate all json files to a language

    Usage: /admin-translate-step-2?language=ro
    """

    def __call__(self):
        return translation_list_type_fields(getSite())


class SomeTranslated(BrowserView):
    """Prepare a list of links for each content type in order to verify
    translation

    Usage: /admin-some-translated?items=10
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return admin_some_translated(getSite(), **kwargs)


class RunTranslationSingleItem(BrowserView):
    """Translate a single item

    To be used for testing translation without waiting for all objects to
    be updated

    Usage: item/admin-translate-this
    """

    def __call__(self):
        obj = self.context
        result = translate_obj(obj)
        # transaction.commit()
        return result


class TranslationStatus(BrowserView):
    """Display the the current versions for all translated objects"""

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)

        if "version" in kwargs:
            return translations_status_by_version(getSite(), **kwargs)

        return translations_status(getSite(), **kwargs)


class TranslateOneObject(BrowserView):
    """Translate one object."""

    def translate(self):
        response = {"error": None, "items": [], "url": None}
        request = getRequest()
        url = request.get("url", None)
        response["url"] = url
        if url:
            site = api.portal.get()
            try:
                obj = site.unrestrictedTraverse("/cca" + url)
            except Exception:
                response["error"] = "NOT FOUND"
                return response

            if "/en/" in obj.absolute_url():
                response["items"] = self.create_translations(obj)
                self.translate_obj(obj)
                # self.set_workflow_states(obj)

                self.copy_interfaces(obj)  # TODO: delete. It's included in
                # create_translation_object. It is used here only for testing
                # on old created content. Example: fixing interfaces for pages
                # like share-your-info

                self.copy_fields(obj)
            else:
                response["error"] = "/en/ not found in url"
        return response

    def get_url(self):
        return self.request.form["url"]

    def error(self, obj, error):
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = utils.pretty_title_or_id(obj, obj)
            message = _(
                "Unable to translate ${name} as part of content rule "
                "'translate' action: ${error}",
                mapping={"name": title, "error": error},
            )
            IStatusMessage(request).addStatusMessage(message, type="error")

    def create_translations(self, obj):
        response = []
        """ Make sure all translations (cloned) objs exists for this obj
        """
        transaction.savepoint()
        translations = TranslationManager(obj).get_translations()
        for language in get_site_languages():
            if language != "en" and language not in translations:
                try:
                    create_translation_object(obj, language)
                except Exception:
                    pass
            if language != "en":
                response.append(obj.absolute_url())
        transaction.commit()
        return response

    def translate_obj(self, obj):
        """Send the obj to be translated"""
        try:
            translate_obj(obj, one_step=True)
        except Exception as e:
            self.error(obj, str(e))

    def copy_interfaces(self, obj):
        """Copy interfaces from en to translated obj"""
        translations = TranslationManager(obj).get_translations()
        for language in translations:
            trans_obj = translations[language]
            copy_missing_interfaces(obj, trans_obj)

    def set_workflow_states(self, obj):
        """Mark translations as not approved"""
        translations = TranslationManager(obj).get_translations()
        for language in translations:
            this_obj = translations[language]
            wftool = getToolByName(this_obj, "portal_workflow")
            wftool.doActionFor(this_obj, "send_to_translation_not_approved")

    def copy_fields(self, obj):
        """Run step 4 for this obj"""
        translations = TranslationManager(obj).get_translations()
        for language in translations:
            if language != "en":
                settings = {
                    "language": language,
                    "uid": obj.UID(),
                }
                translation_step_4(getSite(), settings)


# @adapter(Interface, ITranslateAction, Interface)
# @implementer(IExecutable)
