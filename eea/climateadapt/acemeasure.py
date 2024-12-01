""" CaseStudy and AdaptationOption implementations
"""

import json
import logging
from datetime import date

from eea.climateadapt.behaviors import (IAdaptationOption,
                                        ICaseStudy)
from eea.climateadapt.interfaces import IClimateAdaptContent
from eea.climateadapt.sat.datamanager import queue_callback
from eea.climateadapt.sat.handlers import HANDLERS
from eea.climateadapt.sat.settings import get_settings
# from eea.climateadapt.sat.utils import _measure_id, to_arcgis_coords
from eea.climateadapt.utils import _unixtime, shorten
from eea.climateadapt.vocabulary import BIOREGIONS
# from eea.rabbitmq.plone.rabbitmq import queue_msg
from plone.api.portal import get_tool
from plone.dexterity.content import Container
from zope.interface import implementer

logger = logging.getLogger("eea.climateadapt.acemeasure")

@implementer(IAdaptationOption, IClimateAdaptContent)
class AdaptationOption(Container):
    """The AdaptationObject content type."""

    search_type = "MEASURE"

@implementer(ICaseStudy, IClimateAdaptContent)
class CaseStudy(Container):

    search_type = "ACTION"

    def _short_description(self):
        v = self.long_description
        html = v and v.output.strip() or ""

        if html:
            portal_transforms = get_tool(name="portal_transforms")
            data = portal_transforms.convertTo("text/plain", html, mimetype="text/html")
            html = shorten(data.getData(), to=100)

        return html

    def _get_area(self):
        if not self.geochars:
            return ""

        try:
            chars = json.loads(self.geochars)
            els = chars["geoElements"]

            if "biotrans" not in list(els.keys()):
                return ""
            bio = els["biotrans"]

            if not bio:
                return ""
            bio = BIOREGIONS[bio[0]]  # NOTE: we take the first one

            return bio
        except Exception:
            logger.exception(
                "Error getting biochar area for case study %s", self.absolute_url()
            )

            return ""

    # def _repr_for_arcgis(self):
    #     is_featured = getattr(self, "featured", False)
    #     # is_highlight = getattr(self, 'highlight', False)
    #     # classes = {
    #     #     (False, False): 'normal',
    #     #     (True, False): 'featured',
    #     #     (True, True): 'featured-highlight',
    #     #     (False, True): 'highlight',
    #     # }
    #     # client_cls = classes[(is_featured, is_highlight)]
    #     client_cls = is_featured and "featured" or "normal"

    #     if self.geolocation and self.geolocation.latitude:
    #         geo = to_arcgis_coords(
    #             self.geolocation.longitude, self.geolocation.latitude
    #         )
    #         geometry = {
    #             "x": geo[0],
    #             "y": geo[1],
    #         }
    #     else:
    #         geometry = {"x": "", "y": ""}

    #     if self.effective_date is not None:
    #         if hasattr(self.effective_date, "date"):
    #             effective = self.effective_date.date()
    #         else:
    #             effective = self.effective_date.asdatetime().date()
    #     else:
    #         effective = date.today()  # todo? item not published?

    #     today = date.today()
    #     timedelta = today - effective

    #     if timedelta.days > 90:
    #         newitem = "no"
    #     else:
    #         newitem = "yes"

    #     res = {
    #         "attributes": {
    #             "area": self._get_area(),
    #             "itemname": self.Title(),
    #             "desc_": self._short_description(),
    #             "website": self.websites and self.websites[0] or "",
    #             "sectors": ";".join(self.sectors or []),
    #             "risks": ";".join(self.climate_impacts or []),
    #             "measureid": getattr(self, "_acemeasure_id", "") or self.UID(),
    #             "featured": is_featured and "yes" or "no",
    #             "newitem": newitem,
    #             "casestudyf": "CASESEARCH;",  # TODO: implement this
    #             "client_cls": client_cls,
    #             "Creator": self.creators[-1],
    #             "CreationDate": _unixtime(self.creation_date),
    #             "EditDate": _unixtime(self.modification_date),
    #             "Editor": self.workflow_history["cca_items_workflow"][-1]["actor"],
    #             "EffectiveDate": _unixtime(self.effective_date),
    #         },
    #         "geometry": geometry,
    #     }

    #     return res


def handle_for_arcgis_sync(obj, event):
    """Dispatch event to RabbitMQ to trigger synchronization to ArcGIS"""
    event_name = event.__class__.__name__
    uid = _measure_id(obj)
    msg = "{0}|{1}".format(event_name, uid)
    logger.info("Queuing RabbitMQ message: %s", msg)

    settings = get_settings()

    if settings.skip_rabbitmq:
        queue_callback(lambda: HANDLERS[event_name](obj, uid))

        return

    try:
        # queue_msg(msg, queue="eea.climateadapt.casestudies")
        pass
    except Exception:
        logger.exception("Couldn't queue RabbitMQ message for case study event")


def handle_measure_added(obj, event):
    """Assign a new measureid to this AceMeasure"""

    catalog = get_tool(name="portal_catalog")
    ids = sorted(
        value
        for value in catalog.uniqueValuesFor("acemeasure_id")
        if value)
    obj._acemeasure_id = ids[-1] + 1
    obj.reindexObject(idxs=["acemeasure_id"])


# this was to fix (probably) a bug in plone.app.widgets. This fix is no longer
# needed with plone.app.widgets 1.10.dev4
# @adapter(getSpecification(ICaseStudy['adaptationoptions']), IWidgetsLayer)
# @implementer(IFieldWidget)
# def AdaptationOptionsFieldWidget(field, request):
#     """ The vocabulary view is overridden so that
#         the widget will show only adaptation options
#         Check browser/overrides.py for more details
#     """
#     import pdb
#     pdb.set_trace()
#     widget = FieldWidget(field, RelatedItemsWidget(request))
#     widget.vocabulary = 'eea.climateadapt.adaptation_options'
#     widget.vocabulary_override = True
#
#     return widget

# from z3c.relationfield.schema import RelationChoice
# from collective import dexteritytextindexer
# from eea.climateadapt import MessageFactory as _
# from plone.app.contenttypes.interfaces import IImage
# from plone.app.textfield import RichText
# from plone.autoform import directives
# from plone.formwidget.contenttree import ObjPathSourceBinder
# from plone.namedfile.field import NamedBlobImage
# from plone.namedfile.interfaces import IImageScaleTraversable
# from z3c.form.browser.textlines import TextLinesWidget
# from eea.climateadapt.schema import Year
# from eea.climateadapt.schema import Date
# from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
#                          TextLine, Tuple)
#
