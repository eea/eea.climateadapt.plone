import logging
from operator import itemgetter

import DateTime
import transaction
from collective.exportimport.export_content import ExportContent
from collective.exportimport.export_other import ExportOrdering
from collective.exportimport.import_content import ImportContent
from collective.exportimport.import_other import ImportTranslations, link_translations
from OFS.interfaces import IOrderedContainer
from plone import api
from plone.dexterity.utils import resolveDottedName
from plone.restapi.interfaces import IJsonCompatible
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides, directlyProvidedBy

from eea.climateadapt.interfaces import (
    IBalticRegionMarker,
    ICCACountry,
    IMainTransnationalRegionMarker,
    ITransnationalRegionMarker,
)

ANNOTATIONS_TO_EXPORT = ["c3s_json_data", "broken_links_data"]
ANNOTATIONS_KEY = "exportimport.annotations"

logger = logging.getLogger(__name__)

MARKER_INTERFACES_TO_EXPORT = [
    ITransnationalRegionMarker.__identifier__,
    IBalticRegionMarker.__identifier__,
    IMainTransnationalRegionMarker.__identifier__,
    ICCACountry.__identifier__,
]
MARKER_INTERFACES_KEY = "exportimport.marker_interfaces"


class CustomExportContent(ExportContent):
    def update_query(self, query):
        _from = self.request.form.get("from")
        if _from:
            _from = int(_from)
            date = DateTime.DateTime() - _from
            query["modified"] = {"query": date, "range": "min"}

        return query

    def global_dict_hook(self, item, obj):
        item = self.export_marker_interfaces(item, obj)
        item = self.export_annotations(item, obj)
        return item

    def export_marker_interfaces(self, item, obj):
        interfaces = [i.__identifier__ for i in directlyProvidedBy(obj)]
        interfaces = [
            i for i in interfaces if i in MARKER_INTERFACES_TO_EXPORT]
        if interfaces:
            item[MARKER_INTERFACES_KEY] = interfaces
        return item

    def export_annotations(self, item, obj):
        results = {}
        annotations = IAnnotations(obj)
        for key in ANNOTATIONS_TO_EXPORT:
            data = annotations.get(key)
            if data:
                results[key] = IJsonCompatible(data, None)
        if results:
            item[ANNOTATIONS_KEY] = results
        return item


class CustomImportContent(ImportContent):
    def global_obj_hook(self, obj, item):
        item = self.import_annotations(obj, item)
        return item

    def import_annotations(self, obj, item):
        annotations = IAnnotations(obj)
        for key in item.get(ANNOTATIONS_KEY, []):
            annotations[key] = item[ANNOTATIONS_KEY][key]
        return item

    def global_obj_hook_before_deserializing(self, obj, item):
        """Apply marker interfaces before deserializing."""
        for iface_name in item.pop(MARKER_INTERFACES_KEY, []):
            try:
                iface = resolveDottedName(iface_name)
                if not iface.providedBy(obj):
                    alsoProvides(obj, iface)
                    logger.info(
                        "Applied marker interface %s to %s",
                        iface_name,
                        obj.absolute_url(),
                    )
            except ModuleNotFoundError:
                logger.info("Unable to import marker interface %s", iface)
        return obj, item


class FixedExportOrdering(ExportOrdering):
    def all_orders(self):
        results = []

        def get_position_in_parent(obj, path):
            uid = IUUID(obj, None)
            if not uid:
                return
            parent = obj.__parent__
            ordered = IOrderedContainer(parent, None)
            if ordered is not None:
                try:
                    order = ordered.getObjectPosition(obj.getId())
                except ValueError:
                    order = None
                if order is not None:
                    results.append({"uuid": uid, "order": order})
                # cat src/collective.exportimport/src/collective/exportimport/export_other.py
                # order = ordered.getObjectPosition(obj.getId())
                # if order is not None:
                #     results.append({"uuid": uid, "order": order})
            return

        portal = api.portal.get()
        portal.ZopeFindAndApply(
            portal, search_sub=True, apply_func=get_position_in_parent
        )
        return sorted(results, key=itemgetter("order"))


class CustomImportTranslations(ImportTranslations):
    """"""

    def import_translations(self, data):
        imported = 0
        empty = []
        less_than_2 = []
        for translationgroup in data:
            if len(translationgroup) < 2:
                continue

            # Make sure we have content to translate
            tg_with_obj = {}
            for lang, uid in translationgroup.items():
                obj = api.content.get(UID=uid)
                if obj:
                    tg_with_obj[lang] = obj
                else:
                    # logger.info(f'{uid} not found')
                    continue
            if not tg_with_obj:
                empty.append(translationgroup)
                continue

            if len(tg_with_obj) < 2:
                less_than_2.append(translationgroup)
                logger.info("Only one item: {}".format(translationgroup))
                continue

            imported += 1
            for index, (lang, obj) in enumerate(tg_with_obj.items()):
                if index == 0:
                    canonical = obj
                else:
                    translation = obj
                    link_translations(canonical, translation, lang)

            logger.info("Imported translation group nr. {}".format(imported))

            if not imported % 1000:
                msg = "Committing after importing {} translations...".format(
                    imported)
                logger.info(msg)
                transaction.get().note(msg)
                transaction.commit()

        logger.info(
            "Imported {} translation-groups. For {} groups we found only one item. {} groups without content dropped".format(
                imported, len(less_than_2), len(empty)
            )
        )
