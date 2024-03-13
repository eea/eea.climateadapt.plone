""" Admin translation
"""

from Products.CMFCore.utils import getToolByName
import transaction
from eea.climateadapt.asynctasks.utils import get_async_service
from eea.climateadapt.translation.utils import (
    get_current_language,
    get_site_languages,
)
from Products.CMFPlone import utils
from plone import api
from plone.api import portal
from .core import (
    admin_some_translated,
    copy_missing_interfaces,
    create_translation_object,
    execute_trans_script,
    execute_translate_async,
    fix_urls_for_translated_content,
    initiate_translations,
    report_unlinked_translation,
    translate_obj,
    translation_list_type_fields,
    translation_repaire,
    translation_repaire_step_3,
    translation_step_1,
    translation_step_2,
    translation_step_3,
    translation_step_4,
    translation_step_5,
    translations_status,
    translations_status_by_version,
    verify_cloned_language,
    verify_translation_fields,
    verify_unlinked_translation,
)
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.globalrequest import getRequest
from zope.site.hooks import getSite
from plone.app.multilingual.manager import TranslationManager

import logging

logger = logging.getLogger("eea.climateadapt")


class PrepareTranslation(BrowserView):
    """Clone the content to be available for a new translation
    Usage: /admin-prepare-translation?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return execute_trans_script(getSite(), **kwargs)


class VerifyUnlinkedTranslation(BrowserView):
    """Check items which does not have relation to english
    Usage: /admin-verify-unlinked-translation
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return verify_unlinked_translation(getSite(), self.request)


class ReportUnlinkedTranslation(BrowserView):
    """Check items which does not have relation to english
    Usage: /admin-report-unlinked-translation
    """

    def report(self, **kwargs):
        kwargs.update(self.request.form)
        return report_unlinked_translation(getSite(), self.request)


class VerifyClonedLanguage(BrowserView):
    """Use this view to check all links for a new cloned language
    Usage: /admin-verify-cloned?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return verify_cloned_language(getSite(), **kwargs)


class VerifyTranslationFields(BrowserView):
    """Use this view to check all links for a new cloned language
    Usage: /admin-verify-translation-fields?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return verify_translation_fields(getSite(), self.request)


class FixUrlsForTranslatedContent(BrowserView):
    """Use this view to check all links for a new cloned language
    Usage: /admin-fix-urls-translated-content?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return fix_urls_for_translated_content(getSite(), **kwargs)


class TranslateStep1(BrowserView):
    """Use this view to get a json files for all eng objects
    Usage: /admin-translate-step-1?limit=10&search_path=some-words-in-url
    Limit and search_path params are optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_1(getSite(), self.request)


class TranslateStep2(BrowserView):
    """Use this view to translate all json files to a language
    Usage: /admin-translate-step-2-old?language=ro&uid=ABCDEF
    uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_2(getSite(), self.request)


class TranslateStep3(BrowserView):
    """Use this view to save the values from annotation in objects fields
    Usage: /admin-translate-step-3?language=ro&uid=ABCDEF
    uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_3(getSite(), self.request)


class TranslateStep4(BrowserView):
    """Use this view to copy fields values that are language independent
    Usage: /admin-translate-step-4?language=ro&uid=ABCDEF
    uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_4(getSite(), self.request)


class TranslateStep5(BrowserView):
    """Use this view to publish all translated items for a language
    and copy the publishing and creation date from EN items.
    Usage: /admin-translate-step-5?language=ro&uid=ABCDEF
    uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_5(getSite(), self.request)


class TranslateRepaire(BrowserView):
    """Use this view to save the values from annotation in objects fields
    Usage: /admin-translate-repaire?language=es&file=ABCDEF
    file : /tmp/[ABCDEF].json
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_repaire(getSite(), self.request)


class TranslateRepaireStep3(BrowserView):
    """Use this view to save the values from annotation in objects fields
    Usage: /admin-translate-repaire-step-3?language=es&file=ABCDEF
    file : /tmp/[ABCDEF].json
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_repaire_step_3(getSite(), self.request)


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


class RunTranslation(BrowserView):
    """Translate the contents
    Usage:
    /admin-run-translation?language=it&version=1&skip=1200  -skip 1200 objs
    /admin-run-translation?language=it&version=1
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return initiate_translations(getSite(), **kwargs)


class RunTranslationSingleItem(BrowserView):
    """Translate a single item
    Usage: item/admin-translate-this

    To be used for testing translation without waiting for all objects to
    be updated
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


class AdminPublishItems(BrowserView):
    """Publish the items needed for frontpage to work
    news, events, countries-regions
    """

    items_to_publish = [
        "frontpage-slides",
        "more-events",
        # 'countries-regions',
        # 'countries-regions/index_html',
        "news-archive",
        "countries-regions/countries",
    ]

    @property
    def site(self):
        site = portal.getSite()

        return site

    @property
    def wftool(self):
        wftool = portal.get_tool("portal_workflow")

        return wftool

    def get_object_by_path(self, path):
        try:
            obj = self.site.restrictedTraverse(path)
        except:
            logger.info("Path not found: %s" % path)

            return None

        return obj

    def publish_obj(self, obj):
        if api.content.get_state(obj) != "published":
            logger.info("Publishing %s" % obj.absolute_url())
            try:
                self.wftool.doActionFor(obj, "publish")
            except:
                return obj.absolute_url()

    def __call__(self):
        errors = []

        for item in self.items_to_publish:
            en_path = "en/{}".format(item)
            obj_en = self.get_object_by_path(en_path)

            if not obj_en:
                continue

            # skip if english item is not published
            if api.content.get_state(obj_en) != "published":
                continue

            translations = TranslationManager(obj_en).get_translations()

            # first step: publish the item
            for language in translations.keys():
                transl_path = "{}/{}".format(language, item)
                obj_transl = self.get_object_by_path(transl_path)

                if not obj_transl:
                    continue

                result = self.publish_obj(obj_transl)
                if result:
                    errors.append(result)

            # second step: publish the contents of the item
            for _, content_obj in obj_en.contentItems():
                try:
                    if api.content.get_state(content_obj) != "published":
                        continue
                except:
                    continue

                translations = TranslationManager(content_obj).get_translations()

                for _, _obj_transl in translations.items():
                    result = self.publish_obj(_obj_transl)

                    if result:
                        errors.append(result)

        return "<br>".join(errors)


# @adapter(Interface, ITranslateAction, Interface)
# @implementer(IExecutable)
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
            except:
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
                except Exception as err:
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


class TranslateObjectAsync(BrowserView):
    @property
    def async_service(self):
        return get_async_service()

    def __call__(self):
        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")
        obj = self.context
        options = {}
        options["obj_url"] = obj.absolute_url()
        options["uid"] = obj.UID()
        options["http_host"] = self.context.REQUEST.environ["HTTP_X_FORWARDED_HOST"]

        request_vars = {
            # 'PARENTS': obj.REQUEST['PARENTS']
        }

        # request_keys_to_copy = ['_orig_env', 'environ', 'other', 'script']
        # for req_key in request_keys_to_copy:
        #     request_vars[req_key] = getattr(obj.REQUEST, req_key)

        if "/en/" in obj.absolute_url():
            # run translate FULL (all languages)
            for language in get_site_languages():
                if language == "en":
                    continue

                if self.async_service is None:
                    logger.warn("Can't translate_asyn, plone.app.async not installed!")
                    return

                create_translation_object(obj, language)
                queue = self.async_service.getQueues()[""]
                self.async_service.queueJobInQueue(
                    queue,
                    ("translate",),
                    execute_translate_async,
                    obj,
                    options,
                    language,
                    request_vars,
                )

        else:
            language = get_current_language(self.context, self.request)
            en_path = "/".join(obj.getPhysicalPath())
            en_path = en_path.replace("/{}/".format(language), "/en/")
            obj_en = self.context.unrestrictedTraverse(
                en_path.replace("/{}/".format(language), "/en/")
            )

            create_translation_object(obj_en, language)
            queue = self.async_service.getQueues()[""]
            self.async_service.queueJobInQueue(
                queue,
                ("translate",),
                execute_translate_async,
                obj_en,
                options,
                language,
                request_vars,
            )

        self.request.response.redirect(obj.absolute_url())
