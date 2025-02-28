from plone.api.portal import get_tool
from plone.app.layout.viewlets import ViewletBase
from plone.app.multilingual.manager import TranslationManager
from eea.climateadapt.translation.utils import get_current_language, translate_text


class TranslationInfoViewlet(ViewletBase):
    """Display translation info for current object"""

    def get_language(self):
        return get_current_language(self.context, self.request)

    def is_translated_content(self):
        obj_language = self.get_language()
        if obj_language == "en":
            return False
        try:
            translations = TranslationManager(self.context).get_translations()
            trans_obj = translations.get(obj_language)
            if trans_obj is not None:
                url = trans_obj.absolute_url()
                actual_url = self.request.get("ACTUAL_URL")
                if url == actual_url:
                    return True

                if "folder_contents" in actual_url:
                    return False

                return True
        except Exception:
            return False


class TranslationStateViewlet(ViewletBase):
    """Display the translation state"""

    trans_wf_id = "cca_translations_workflow"
    css_types = {
        "not_translated": "error",
        "translation_not_approved": "warning",
        "translation_approved": "info",
    }

    def show_approve_button(self):
        context = self.context
        state, _ = self._get_current_wf_state(context)

        return state == "translation_not_approved"

    def get_css_class(self):
        context = self.context
        css_class = "portalMessage {}"
        state, _ = self._get_current_wf_state(context)
        css_type = self.css_types.get(state, "no_state")

        return css_class.format(css_type)

    def _get_current_wf_state(self, context=None):
        if context is None:
            context = self.context

        wftool = get_tool("portal_workflow")
        wf = None

        for _wf in wftool.getWorkflowsFor(context):
            if _wf.id != self.trans_wf_id:
                continue

            wf = _wf

        if not wf:
            return "Translation state not found", None

        initial_state = wf.initial_state
        state = wftool.getStatusOf(
            "cca_translations_workflow", self.context) or {}
        state = state.get("review_state", initial_state)
        wf_state = wf.states[state]

        return state, wf_state

    def get_status(self, context=None):
        state, wf_state = self._get_current_wf_state(context)
        title = wf_state and wf_state.title.strip() or state

        return title

    def get_transitions(self, context=None):
        if not context:
            context = self.context

        wftool = get_tool("portal_workflow")
        transitions = wftool.listActionInfos(object=context)
        return [t for t in transitions if t["allowed"]]


class TranslationCheckLanguageViewlet(ViewletBase):
    """Display if we have translation for language set in cookie"""

    def show_display_message(self):
        if self.get_plone_language() != self.get_cookie_language():
            # check if force to stay on this page
            if self.request.get("langflag", None):
                return True
            url = self.get_suggestion_url()

            if "++aq++" in self.request["ACTUAL_URL"]:
                url = (url or "").replace(
                    "/news-archive/", "/observatory/++aq++news-archive/"
                )
            # if we have a url, then redirect. A few pages are not translated
            if url:
                return self.request.response.redirect(url)
            return True
        return None

    def get_message(self, message):
        return translate_text(
            self.context, self.request, message, "eea.cca", self.get_cookie_language()
        )

    def get_plone_language(self):
        return get_current_language(self.context, self.request)

    def get_cookie_language(self):
        """Cookie language if set, else item's language, else EN"""
        cookie_language = self.request.cookies.get("I18N_LANGUAGE", None)
        if cookie_language is not None and len(cookie_language) > 1:
            return cookie_language

        obj_language = getattr(self.context, "language", None)
        if obj_language is not None and len(obj_language) > 1:
            return obj_language

        return "en"

    def get_suggestion_url(self):
        try:
            translations = TranslationManager(self.context).get_translations()
        except Exception:
            return None
        cookie_language = self.get_cookie_language()
        if cookie_language in translations:
            return translations[cookie_language].absolute_url()
        return None
