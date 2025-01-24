import logging
from collective.exportimport.export_content import ExportContent
from collective.exportimport.import_content import ImportContent
from zope.interface import directlyProvidedBy

from plone.restapi.interfaces import IJsonCompatible
from plone.dexterity.utils import resolveDottedName
from zope.interface import alsoProvides
from eea.climateadapt.interfaces import (
    ITransnationalRegionMarker,
    IMainTransnationalRegionMarker,
    IBalticRegionMarker,
    ICCACountry,
)
from zope.annotation.interfaces import IAnnotations

ANNOTATIONS_TO_EXPORT = [
    "",
]
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
    def global_dict_hook(self, item, obj):
        item = self.export_marker_interfaces(item, obj)
        item = self.export_annotations(item, obj)
        return item

    def export_marker_interfaces(self, item, obj):
        interfaces = [i.__identifier__ for i in directlyProvidedBy(obj)]
        interfaces = [i for i in interfaces if i in MARKER_INTERFACES_TO_EXPORT]
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


# from operator import itemgetter
# from collective.exportimport.export_other import ExportOrdering
# from OFS.interfaces import IOrderedContainer
# from plone import api
# from plone.uuid.interfaces import IUUID

# class FixedExportOrdering(ExportOrdering):
#     def all_orders(self):
#         results = []
#
#         def get_position_in_parent(obj, path):
#             uid = IUUID(obj, None)
#             if not uid:
#                 return
#             try:
#                 parent = obj.__parent__
#                 ordered = IOrderedContainer(parent, None)
#                 if ordered is not None:
#                     order = ordered.getObjectPosition(obj.getId())
#                     if order is not None:
#                         results.append({"uuid": uid, "order": order})
#             except Exception as e:
#                 logger.debug(
#                     "Could not get item position in parent: %s for %s, %s", obj, path, e
#                 )
#             return
#
#         portal = api.portal.get()
#         portal.ZopeFindAndApply(
#             portal, search_sub=True, apply_func=get_position_in_parent
#         )
#         return sorted(results, key=itemgetter("order"))
