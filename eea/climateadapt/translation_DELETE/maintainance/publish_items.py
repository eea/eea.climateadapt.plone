from plone.app.multilingual.manager import TranslationManager
from plone import api
from plone.api import portal
from Products.Five.browser import BrowserView
import logging

logger = logging.getLogger("eea.climateadapt")


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
        except Exception:
            logger.info("Path not found: %s" % path)

            return None

        return obj

    def publish_obj(self, obj):
        if api.content.get_state(obj) != "published":
            logger.info("Publishing %s" % obj.absolute_url())
            try:
                self.wftool.doActionFor(obj, "publish")
            except Exception:
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
            for language in list(translations.keys()):
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
                except Exception:
                    continue

                translations = TranslationManager(content_obj).get_translations()

                for _, _obj_transl in list(translations.items()):
                    result = self.publish_obj(_obj_transl)

                    if result:
                        errors.append(result)

        return "<br>".join(errors)
