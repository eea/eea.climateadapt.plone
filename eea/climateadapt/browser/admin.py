# -*- coding: utf-8 -*-
import csv
import datetime
import json
import logging
from io import BytesIO as StringIO

from apiclient.discovery import build
from DateTime import DateTime
from eea.rdfmarshaller.actions.pingcr import ping_CRSDS
from lxml.etree import fromstring
from oauth2client.service_account import ServiceAccountCredentials
from pkg_resources import resource_filename
from plone import api
from plone.api import portal
from plone.api.portal import get_tool, getSite
from plone.app.registry.browser.controlpanel import (ControlPanelFormWrapper,
                                                     RegistryEditForm)
from plone.app.widgets.dx import RelatedItemsWidget
from plone.app.widgets.interfaces import IWidgetsLayer
from plone.dexterity.utils import datify
from plone.directives import form
from plone.i18n.normalizer import idnormalizer
from plone.indexer.interfaces import IIndexer
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from six.moves.html_parser import HTMLParser
from z3c.form import button
from z3c.form import form as z3cform
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter, getMultiAdapter, getUtility
from zope.interface import (Interface, Invalid, implementer, implements,
                            invariant)
from zope.site.hooks import getSite

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.blocks import BlocksTraverser, BlockType
from eea.climateadapt.browser.fixblobs import (check_at_blobs,
                                               check_dexterity_blobs)
from eea.climateadapt.browser.migrate import DB_ITEM_TYPES
from eea.climateadapt.browser.site import _extract_menu
from eea.climateadapt.interfaces import IGoogleAnalyticsAPI
from eea.climateadapt.scripts import get_plone_site

# from collections import defaultdict

html_unescape = HTMLParser().unescape

logger = logging.getLogger("eea.climateadapt")


def force_unlock(context):
    annot = getattr(context, "__annotations__", {})

    if hasattr(context, "_dav_writelocks"):
        del context._dav_writelocks
        context._p_changed = True

    if "plone.locking" in annot:
        del annot["plone.locking"]

        context._p_changed = True
        annot._p_changed = True


class CheckCopyPasteLocation(BrowserView):
    """Performs a check which doesn't allow user to Copy cca-items
    if they belong to the group extranet-cca-editors
    """

    def __call__(self, action, object):
        return self.check(action, object)

    @view.memoize
    def check(self, action, object):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )

        member = portal_state.member()

        try:
            if member.name == "Anonymous User":
                return False
        except Exception:
            pass  # 161069 Error while rendering plone.contentactions

        user = portal_state.member().getUser().getId()
        groups = getToolByName(self, "portal_groups").getGroupsByUserId(user)

        for group in groups:
            if not group:
                continue
            if (
                group.id == "extranet-cca-editors"
                and "metadata" in self.context.getPhysicalPath()
            ):
                logger.info("Can't Copy: returning False")

                return False

        return True


class InvalidMenuConfiguration(Invalid):
    __doc__ = "The menu format is invalid"


class IMainNavigationMenu(form.Schema):
    menu = schema.Text(title=unicode("Menu structure text"), required=True)

    @invariant
    def check_menu(data):
        try:
            _extract_menu(data.menu)
        except Exception as e:
            raise InvalidMenuConfiguration(e)


class MainNavigationMenuEdit(form.SchemaForm):
    """A page to edit the main site navigation menu"""

    schema = IMainNavigationMenu
    ignoreContext = False

    label = "Fill in the content of the main menu"
    description = """This should be a structure for the main menu. Use a single
    empty line to separate main menu entries. All lines after the main menu
    entry, and before an empty line, will form entries in that section menu. To
    create a submenu for a section, start a line with a dash (-).  Links should
    start with a slash (/)."""

    @property
    def ptool(self):
        return getToolByName(self.context, "portal_properties")["site_properties"]

    @view.memoize
    def getContent(self):
        content = {"menu": self.ptool.getProperty("main_navigation_menu")}

        return content

    @button.buttonAndHandler(unicode("Save"))
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return

        self.ptool._updateProperty("main_navigation_menu", data["menu"])

        self.status = "Saved, please check."


class HealthNavigationMenuEdit(form.SchemaForm):
    """A page to edit the main site navigation menu"""

    schema = IMainNavigationMenu
    ignoreContext = False

    label = "Fill in the content of the health navigation menu"
    description = """This should be a structure for health menu. Use a single
    empty line to separate main menu entries. All lines after the main menu
    entry, and before an empty line, will form entries in that section menu. To
    create a submenu for a section, start a line with a dash (-).  Links should
    start with a slash (/)."""

    @property
    def ptool(self):
        return getToolByName(self.context, "portal_properties")["site_properties"]

    @view.memoize
    def getContent(self):
        content = {"menu": self.ptool.getProperty("health_navigation_menu")}

        return content

    @button.buttonAndHandler(unicode("Save"))
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return

        self.ptool._updateProperty("health_navigation_menu", data["menu"])

        self.status = "Saved, please check."


class ForceUnlock(BrowserView):
    """Forcefully unlock a content item"""

    def __call__(self):
        annot = getattr(self.context, "__annotations__", None)

        if hasattr(self.context, "_dav_writelocks"):
            del self.context._dav_writelocks
            self.context._p_changed = True

        if annot is None:
            return

        if "plone.locking" in annot:
            del annot["plone.locking"]

            self.context._p_changed = True
            annot._p_changed = True

        url = self.context.absolute_url()
        props_tool = getToolByName(self.context, "portal_properties")

        if props_tool:
            types_use_view = props_tool.site_properties.typesUseViewActionInListings

            if self.context.portal_type in types_use_view:
                url += "/view"

        return self.request.RESPONSE.redirect(url)


class ListTilesWithTitleView(BrowserView):
    """View that lists all tiles with richtext title and their respective urls"""

    def __call__(self):
        covers = self.context.portal_catalog.searchResults(
            portal_type="collective.cover.content"
        )
        self.urls = []

        for cover in covers:
            cover = cover.getObject()

            self.tiles = []

            self.walk(json.loads(cover.cover_layout))

            if hasattr(cover, "__annotations__"):
                for tile_id in self.tiles:
                    tile_id = tile_id.encode()
                    self.urls.append(cover.absolute_url())

        return self.index()

    @view.memoize
    def linkify(self, text):
        if not text:
            return

        if text.startswith("/") or text.startswith("http"):
            return text

        return "http://" + text

    def walk(self, item):
        if isinstance(item, dict):
            if item.get("tile-type") == "eea.climateadapt.richtext_with_title":
                self.tiles.append(item["id"])

            self.walk(item.get("children", []))
        elif isinstance(item, list):
            for x in item:
                self.walk(x)


class ForcePingObjectCRView(BrowserView):
    """Force pingcr on objects between a set interval"""

    def __call__(self):
        # cat = get_tool('portal_catalog')
        obj = self.context

        # query = {
        #     'review_state': ['published', 'archived']       ## , 'private'
        # }
        # results = cat.searchResults(query)
        # logger.info("Found %s objects " % len(results))

        # count = 0
        options = {}
        options["create"] = False
        options["service_to_ping"] = "http://semantic.eea.europa.eu/ping"
        # context = res.getObject()
        url = obj.absolute_url()

        if "https" in url:
            url = url.replace("https", "http")

        options["obj_url"] = url + "/@@rdf"
        logger.info("Pinging: %s", url)
        ping_CRSDS(obj, options)
        logger.info("Finished pinging: %s", url)

        return "Finished"


class ForcePingCRView(BrowserView):
    """Force pingcr on objects between a set interval"""

    def __call__(self):
        cat = get_tool("portal_catalog")

        query = {
            "review_state": ["published", "archived"]  # , 'private'
        }
        results = cat.searchResults(query)

        logger.info("Found %s objects " % len(results))

        count = 0
        options = {}
        options["create"] = False
        options["service_to_ping"] = "http://semantic.eea.europa.eu/ping"
        for res in results:
            context = res.getObject()
            url = res.getURL()

            if "https" in url:
                url = url.replace("https", "http")

            options["obj_url"] = url + "/@@rdf"
            logger.info("Pinging: %s", url)
            ping_CRSDS(context, options)
            logger.info("Finished pinging: %s", url)

            count += 1
            if count % 100 == 0:
                logger.info("Went through %s brains" % count)

        logger.info("Finished pinging all brains")
        return "Finished"


class SpecialTagsInterface(Interface):
    """Marker interface for /tags-admin"""


class SpecialTagsView(BrowserView):
    """Custom view for administration of special tags"""

    implements(SpecialTagsInterface)

    def __call__(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )

        action = self.request.form.get("action", None)
        tag = self.request.form.get("tag", None)

        if portal_state.anonymous():
            return self.index()

        if action:
            getattr(self, "handle_" + action)(tag)

        return self.index()

    @view.memoize
    def special_tags(self):
        return self.context.portal_catalog.uniqueValuesFor("special_tags")

    def get_tag_length(self, tag):
        catalog = self.context.portal_catalog._catalog

        return len(catalog.indexes["special_tags"]._index[tag])

    def handle_delete(self, tag):
        catalog = self.context.portal_catalog

        brains = catalog.searchResults(special_tags=tag)

        for b in brains:
            obj = b.getObject()

            if obj.special_tags:
                if isinstance(obj.special_tags, list):
                    obj.special_tags = [
                        key for key in obj.special_tags if key != tag]
                elif isinstance(obj.special_tags, tuple):
                    obj.special_tags = tuple(
                        key for key in obj.special_tags if key != tag
                    )
                obj.reindexObject()
                obj._p_changed = True
        logger.info("Deleted tag: %s", tag)

    def handle_add(self, tag):
        pass

    def handle_rename(self, tag):
        catalog = self.context.portal_catalog
        newtag = self.request.form.get("newtag", None)

        brains = catalog.searchResults(special_tags=tag)

        for b in brains:
            obj = b.getObject()

            if obj.special_tags:
                if isinstance(obj.special_tags, list):
                    obj.special_tags = [
                        key for key in obj.special_tags if key != tag]
                    obj.special_tags.append(newtag)
                elif isinstance(obj.special_tags, tuple):
                    obj.special_tags = tuple(
                        key for key in obj.special_tags if key != tag
                    )
                    obj.special_tags += (newtag,)
                obj._p_changed = True
                obj.reindexObject()
        logger.info("Finished renaming: %s TO %s", tag, newtag)


class SpecialTagsObjects(BrowserView):
    """Gets the links for the special tags that we get in the request"""

    def __call__(self):
        tag = self.request.form["special_tags"].decode("utf-8")
        tag_obj = [
            b.getURL() + "/edit"
            for b in self.context.portal_catalog.searchResults(special_tags=tag)
        ]

        return json.dumps(tag_obj)


class IAddKeywordForm(form.Schema):
    keyword = schema.TextLine(title=unicode("Keyword:"), required=True)
    ccaitems = RelationList(
        title=unicode("Select where to implement the new keyword"),
        default=[],
        description=unicode("Items related to the keyword:"),
        value_type=RelationChoice(
            title=unicode("Related"), vocabulary="eea.climateadapt.cca_items"
        ),
        required=False,
    )


class AddKeywordForm(form.SchemaForm):
    schema = IAddKeywordForm
    ignoreContext = True

    label = "Add keyword"
    description = """ Enter the new keyword you want to add """

    @button.buttonAndHandler(unicode("Submit"))
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return

        keyword = data.get("keyword", None)
        objects = data.get("ccaitems", [])

        if keyword:
            for obj in objects:
                if isinstance(obj.keywords, (list, tuple)):
                    obj.keywords = list(obj.keywords)
                    obj.keywords.append(keyword)
                    obj._p_changed = True
                    obj.reindexObject()
            self.status = "Keyword added"

            return self.status


@adapter(getSpecification(IAddKeywordForm["ccaitems"]), IWidgetsLayer)
@implementer(IFieldWidget)
def CcaItemsFieldWidget(field, request):
    """The vocabulary view is overridden so that
    the widget will show all cca items
    Check browser/overrides.py for more details
    """
    widget = FieldWidget(field, RelatedItemsWidget(request))
    widget.vocabulary = "eea.climateadapt.cca_items"
    widget.vocabulary_override = True

    return widget


class KeywordsAdminView(BrowserView):
    """Custom view for the administration of keywords"""

    def __call__(self):
        action = self.request.form.get("action", None)
        keyword = self.request.form.get("keyword", None)

        if action:
            getattr(self, "handle_" + action)(keyword)

        return self.index()

    @view.memoize
    def keywords(self):
        if "letter" not in self.request:
            return []

        brains = self.context.portal_catalog.searchResults(path="/cca/en")
        keywords = []
        # keywords = self.context.portal_catalog.uniqueValuesFor('keywords')

        for brain in brains:
            kw = brain.keywords

            if kw:
                keywords.extend(list(kw))

        keywords = set(keywords)
        letter = self.request.letter

        if letter == "All":
            return keywords

        res = [k for k in keywords if k.startswith(letter)]

        return res

    @view.memoize
    def keywords_first_letters(self):
        kw = self.context.portal_catalog.uniqueValuesFor("keywords")
        res = sorted(set([k[0] for k in kw if k]))

        return ["All"] + res

    def get_keyword_length(self, key):
        catalog = self.context.portal_catalog._catalog

        return len(catalog.indexes["keywords"]._index[key])

    def handle_delete(self, keyword):
        catalog = self.context.portal_catalog

        brains = catalog.searchResults(keywords=keyword)

        for b in brains:
            obj = b.getObject()

            if obj.keywords:
                if isinstance(obj.keywords, list):
                    obj.keywords = [
                        key for key in obj.keywords if key != keyword]
                elif isinstance(obj.keywords, tuple):
                    obj.keywords = tuple(
                        key for key in obj.keywords if key != keyword)
                obj.reindexObject()
                obj._p_changed = True

        logger.info("Deleted keyword: %s", keyword)
        message = _(
            "Keyword succesfully deleted: ${kw_old}.",
            mapping={"kw_old": keyword},
        )
        IStatusMessage(self.request).addStatusMessage(message, type="success")

        self.request.response.redirect(self.request.URL0)

    def handle_rename(self, keyword):
        catalog = self.context.portal_catalog
        newkeyword = self.request.form.get("newkeyword", None)

        brains = catalog.searchResults(keywords=keyword)

        for b in brains:
            obj = b.getObject()

            if obj.keywords:
                if isinstance(obj.keywords, list):
                    obj.keywords = [
                        key for key in obj.keywords if key != keyword]
                    obj.keywords.append(newkeyword)
                elif isinstance(obj.keywords, tuple):
                    obj.keywords = tuple(
                        key for key in obj.keywords if key != keyword)
                    obj.keywords += (newkeyword,)
                obj._p_changed = True
                obj.reindexObject()

        logger.info("Finished renaming: %s TO %s", keyword, newkeyword)
        message = _(
            "Keyword succesfully renamed: ${kw_old} to ${kw_new}.",
            mapping={"kw_old": keyword, "kw_new": newkeyword},
        )
        IStatusMessage(self.request).addStatusMessage(message, type="success")

        self.request.response.redirect(self.request.URL0)


class KeywordObjects(BrowserView):
    """Gets the links for the keyword that we get in the request"""

    def __call__(self):
        key = self.request.form["keyword"].decode("utf-8")
        brains = self.context.portal_catalog.searchResults(
            keywords=key, path="/cca/en")

        key_obj = [b.getURL() + "/edit" for b in brains]

        return json.dumps(key_obj)


class GoogleAnalyticsAPIEditForm(RegistryEditForm):
    """
    Define form logic
    """

    z3cform.extends(RegistryEditForm)
    schema = IGoogleAnalyticsAPI


ConfigureGoogleAnalyticsAPI = layout.wrap_form(
    GoogleAnalyticsAPIEditForm, ControlPanelFormWrapper
)

ConfigureGoogleAnalyticsAPI.label = "Setup Google Analytics API Integration"


def initialize_analyticsreporting(credentials_data):
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
    An authorized Analytics Reporting API V4 service object.
    """
    SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
    # json_data = json.loads(open(KEY_FILE_LOCATION).read())
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_data, SCOPES
    )

    # Build the service object.

    analytics = build("analyticsreporting", "v4", credentials=credentials)

    return analytics


def custom_report(analytics, view_id):
    now = datetime.datetime.now()

    return (
        analytics.reports()
        .batchGet(
            body={
                "reportRequests": [
                    {
                        "viewId": view_id,
                        "dateRanges": [
                            {
                                "startDate": "2018-04-13",
                                "endDate": now.strftime("%Y-%m-%d"),
                            }
                        ],
                        "metrics": [{"expression": "ga:totalEvents"}],
                        "dimensions": [{"name": "ga:eventLabel"}],
                        "pivots": [
                            {
                                "dimensions": [{"name": "ga:sessionCount"}],
                                "metrics": [{"expression": "ga:users"}],
                            }
                        ],
                        "orderBys": [
                            {"fieldName": "ga:totalEvents",
                                "sortOrder": "DESCENDING"}
                        ],
                        "dimensionFilterClauses": [
                            {
                                "filters": [
                                    {
                                        "dimensionName": "ga:eventCategory",
                                        "expressions": ["database-search"],
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        )
        .execute()
    )


def parse_response(response):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
    response: An Analytics Reporting API V4 response.
    """

    result = {}
    reports = response.get("reports", [])

    if not reports:
        return result

    report = reports[0]

    for row in report.get("data", {}).get("rows", []):
        label = row["dimensions"][0]

        # value = row['metrics'][0]['pivotValueRegions'][0]['values'][0]
        value = row["metrics"][0]["values"][0]

        result[label] = value

    return result


def _refresh_analytics_data(site):
    registry = getUtility(IRegistry, context=site)
    s = registry.forInterface(IGoogleAnalyticsAPI)

    credentials_data = json.loads(s.credentials_json)
    view_id = s.analytics_app_id

    analytics = initialize_analyticsreporting(credentials_data)
    response = custom_report(analytics, view_id)

    res = parse_response(response)

    site.__annotations__["google-analytics-cache-data"] = res
    site.__annotations__._p_changed = True

    import transaction

    transaction.commit()

    return res


def refresh_analytics_data(site=None):
    if site is None:
        site = get_plone_site()
    _refresh_analytics_data(site)


class RefreshGoogleAnalyticsReport(BrowserView):
    """A view to manually refresh google analytics report data"""

    def __call__(self):
        site = portal.get()

        return refresh_analytics_data(site)


class ViewGoogleAnalyticsReport(BrowserView):
    """A view to view the google analytics report data"""

    def __call__(self):
        site = portal.get()

        return str(site.__annotations__.get("google-analytics-cache-data", {}))


class GoPDB(BrowserView):
    def __call__(self):
        import pdb

        pdb.set_trace()
        x = self.context.Creator()


class GetBrokenCreationDates(BrowserView):
    """Get all objects with broken 'creator' and 'creation_date' and fix it
    by getting the creator/creation_date from workflow_history
    """

    zone = DateTime().timezone()
    bl_users = (
        "ghitab",
        "tibiadmin",
        "tibi",
        "tiberich",
        "eugentripon",
        "iulianpetchesi",
        "krisztina",
    )

    def date_to_iso(self, date_time):
        if not date_time:
            return None

        date = datify(date_time)
        return date.toZone(self.zone).ISO()

    def get_new_creator(self, creators, wf_creator):
        if wf_creator not in self.bl_users:
            return wf_creator

        filtered_creators = [x for x in creators if x not in self.bl_users]

        if filtered_creators:
            return filtered_creators[0]

        return ""

    def results(self):
        catalog = api.portal.get_tool("portal_catalog")

        brains = catalog.searchResults(path="/cca/en")
        res = []

        for brain in brains:
            try:
                obj = brain.getObject()
                creator = obj.Creator()
            except:
                continue

            if creator not in self.bl_users:
                continue

            creation_date = obj.CreationDate()
            wfh = obj.workflow_history
            wf_creator = None
            wf_creation_date = None

            wf_data = [
                (x["actor"], x["time"])
                for x in wfh.get("cca_webpages_workflow", {})
                if x["action"] is None
            ]

            if not wf_data:
                wf_data = [
                    (x["actor"], x["time"])
                    for x in wfh.get("cca_items_workflow", {})
                    if x["action"] is None
                ]

            if wf_data:
                wf_creator, wf_creation_date = wf_data[0]

            if not wf_creator:
                continue

            if wf_creator == creator:
                continue

            if self.date_to_iso(wf_creation_date) == creation_date:
                continue

            # if wf_creator in self.bl_users:
            # continue

            if "copy_of_" in obj.absolute_url():
                continue

            new_creator = self.get_new_creator(obj.creators, wf_creator)

            if not new_creator:
                continue

            res.append(
                (obj, creator, wf_creator, new_creator,
                 creation_date, wf_creation_date)
            )

        return res

    def results_string_dates(self):
        catalog = api.portal.get_tool("portal_catalog")

        brains = catalog.searchResults(path="/cca/en")
        res = []

        for brain in brains:
            try:
                obj = brain.getObject()
            except:
                continue

            if not hasattr(obj, "creation_date"):
                continue

            if not isinstance(obj.creation_date, basestring):
                continue

            res.append(obj)

        return res

    def fix_string_dates(self):
        results = self.results_string_dates()

        for obj in results:
            wfh = obj.workflow_history

            new_creation_date = [
                x["time"]
                for x in wfh.get("cca_webpages_workflow", {})
                if x["action"] is None
            ]

            if not new_creation_date:
                new_creation_date = [
                    x["time"]
                    for x in wfh.get("cca_items_workflow", {})
                    if x["action"] is None
                ]

            new_creation_date = new_creation_date and new_creation_date[0] or ""

            if not new_creation_date:
                continue

            obj.creation_date = new_creation_date
            obj._p_changed = True
            obj.reindexObject(idxs=["creators", "creation_date"])

        return "Fixed {} results!".format(len(results))

    def fix_broken_dates(self):
        results = self.results()

        for row in results:
            obj = row[0]

            if obj.portal_type in ("File", "Image"):
                continue

            if check_at_blobs(obj) or check_dexterity_blobs(obj):
                continue

            new_creator = row[3]
            new_creation_date = row[5]
            creators = [x for x in obj.creators if x != new_creator]
            creators = tuple([new_creator] + creators)
            obj.creators = creators
            obj.creation_date = new_creation_date
            obj._p_changed = True
            obj.reindexObject(idxs=["creators", "creation_date"])

        return "Fixed {} objects!".format(len(results))

    def __call__(self):
        if "fix-broken-dates" in self.request.form:
            return self.fix_broken_dates()

        if "fix-string-dates" in self.request.form:
            return self.fix_string_dates()

        if "string-dates" in self.request.form:
            results = self.results_string_dates()

            return [x.absolute_url() for x in results] or "No results!"

        return self.index()


class GetMissingLanguages(BrowserView):
    """Get all objects with missing 'language' field"""

    def results(self):
        catalog = api.portal.get_tool("portal_catalog")

        brains = catalog.searchResults(path="/cca")
        res = []

        for brain in brains:
            try:
                obj = brain.getObject()
            except:
                continue

            language = getattr(obj, "language")

            if language:
                continue

            language_from_path = obj.getPhysicalPath()[2]

            if len(language_from_path) != 2:
                continue

            if language == language_from_path:
                continue

            res.append((obj, language, language_from_path))

        return res

    def fix_languages(self):
        results = self.results()

        for row in results:
            obj = row[0]

            language_from_path = row[2]

            obj.language = language_from_path
            obj._p_changed = True
            obj.reindexObject(idxs=["language"])

        return "Fixed {} objects!".format(len(results))

    def __call__(self):
        if "fix-languages" in self.request.form:
            return self.fix_languages()

        # return "Missing language from {} objects".format(len(self.results()))

        return self.index()


class MigrateTiles(BrowserView):
    def process(self, cover):
        tileids = cover.list_tiles(
            types=["eea.climateadapt.relevant_acecontent"])

        for tid in tileids:
            tile = cover.get_tile(tid)

            if not tile.assigned():
                brains = tile.items()
                uids = [b.UID for b in brains]

                if uids:
                    tile.populate_with_uuids(uids)

                    data_mgr = ITileDataManager(tile)
                    old_data = data_mgr.get()
                    old_data["sortBy"] = "NAME"
                    data_mgr.set(old_data)

                    print(
                        "Fixed cover %s, tile %s with uids %r"
                        % (
                            cover.absolute_url(),
                            tid,
                            uids,
                        )
                    )

                    logger.info(
                        "Fixed cover %s, tile %s with uids %r",
                        cover.absolute_url(),
                        tid,
                        uids,
                    )

    def __call__(self):
        catalog = get_tool("portal_catalog")
        brains = catalog(portal_type="collective.cover.content")

        for brain in brains:
            obj = brain.getObject()
            self.process(obj)

        return "done"


class Item:
    def __init__(self, node):
        self._node = node

    def __getattr__(self, name):
        org_name = name
        name = "field_" + name
        field = self._node.find(name)

        if field is not None:
            return field.text
        if org_name in ["item_id", "item_changed"]:
            field = self._node.find(org_name)
            return field.text
        if org_name in ["sectors", "keywords", "impact", "websites"]:
            return ""
        if org_name in ["governance", "websites"]:
            return []
        if org_name in ["regions"]:
            return {"geoElements": {"element": "EUROPE", "biotrans": []}}
        return None


class AdapteCCACurrentCaseStudyFixImportIDs(BrowserView):
    """AdapteCCA current case study fix import ids"""

    def __call__(self):
        fpath = resource_filename(
            "eea.climateadapt.browser", "data/cases_en_cdata.xml")

        s = open(fpath).read()
        e = fromstring(s)
        container = getSite()["metadata"]["case-studies"]

        for item_node in e.xpath("//item"):
            item_id, field_title = "", ""
            for child in item_node.iterchildren():
                if child.tag == "item_id":
                    item_id = child.text
                if child.tag == "field_title":
                    field_title = idnormalizer.normalize(child.text, None, 500)

            if item_id and field_title:
                annot = IAnnotations(container[field_title])
                annot["import_id"] = item_id

        return "AdapteCCA current case study fixed import_ids"


class ConvertPythonDatetime(BrowserView):
    """Convert effective_date and creation_date from python datetime to
    DateTime
    """

    def __call__(self):
        brains = self.context.portal_catalog.searchResults(wrong_index=True)
        for brain in brains:
            obj = brain.getObject()
            obj = obj.aq_inner.aq_self
            for name in ["creation_date", "effective_date"]:
                attr = getattr(obj, name, None)
                if isinstance(attr, datetime.datetime):
                    setattr(obj, name, DateTime(attr))
                    logger.info("Fix %s: %s - %s", brain.getURL(), name, attr)

        return "done"


class ExportKeywordsCSV(BrowserView):
    """Export the list of keywords and the URLs of items using them"""

    def __call__(self):
        catalog = api.portal.get_tool("portal_catalog")

        res = {}
        for _type in DB_ITEM_TYPES:
            brains = catalog.searchResults(portal_type=_type, path="/cca/en")
            for brain in brains:
                if brain.keywords is None:
                    continue

                for keyword in brain.keywords:
                    if keyword not in res:
                        res[keyword] = []
                    res[keyword].append(brain.getURL())

        out = StringIO()
        csv_writer = csv.writer(out, dialect="excel", delimiter=",")

        for tag in sorted(res.keys()):
            csv_writer.writerow([tag.encode("utf-8"), "\n".join(res[tag])])

        self.request.response.setHeader("Content-type", "text/csv")
        self.request.response.setHeader(
            "Content-Disposition", 'attachment; filename="keywords.csv"'
        )
        out.seek(0)
        return out.getvalue()


class ExportDbItems(BrowserView):
    """Export the list of keywords and the URLs of items using them"""

    def __call__(self):
        catalog = api.portal.get_tool("portal_catalog")

        res = []
        res.append(
            [
                "UID",
                "TITLE",
                "TYPE",
                "URL",
                "KEYWORDS",
                "SECTORS",
                "ELEMENTS",
                "IMPACTS",
                "SearchableText",
                "WEBSITES",
            ]
        )
        for _type in DB_ITEM_TYPES:
            brains = catalog.searchResults(
                portal_type=_type, path="/cca/en", review_state="published"
            )
            for brain in brains:
                line = []
                try:
                    line.append(brain.UID)
                    line.append(brain.Title)
                    line.append(_type.replace("eea.climateadapt.", ""))
                    line.append(brain.getURL())
                    # keywords
                    temp = ""
                    if brain.keywords:
                        temp = ",".join(brain.keywords).encode("utf-8")
                    line.append(temp)

                    obj = brain.getObject()
                    # sectors
                    temp = ""
                    if hasattr(obj, "sectors"):
                        temp = ",".join(obj.sectors)
                    line.append(temp)
                    # elements
                    temp = ""
                    if hasattr(obj, "elements"):
                        if obj.elements:
                            temp = ",".join(obj.elements)
                    line.append(temp)
                    # impacts
                    temp = ""
                    if hasattr(obj, "climate_impacts"):
                        temp = ",".join(obj.climate_impacts)
                    line.append(temp)
                    # searchable text
                    indexer = getMultiAdapter(
                        (obj, catalog), IIndexer, name="SearchableText"
                    )
                    temp = indexer()
                    line.append(temp)
                    # websites
                    temp = ""
                    if hasattr(obj, "websites"):
                        if obj.websites is not None:
                            temp = ",".join(obj.websites)
                    line.append(temp)

                    res.append(line)
                except Exception as Err:
                    import pdb

                    pdb.set_trace()
                    logger.info(brain.getURL())
                    logger.info(Err)

        #        out = StringIO()
        #        csv_writer = csv.writer(out, dialect='excel', delimiter=',')

        logger.info("CSV INIT")
        #        for line in res:
        #            try:
        #                csv_writer.writerow(line)
        #            except:
        #                import pdb; pdb.set_trace()
        #                logger.info(line)

        with open("/tmp/db-items.csv", "w") as outfile:
            csv_writer = csv.writer(outfile, dialect="excel", delimiter=",")
            for line in res:
                try:
                    csv_writer.writerow(line)
                except:
                    import pdb

                    pdb.set_trace()
                    logger.info(line)

        logger.info("CSV PREPARED")

        #        self.request.response.setHeader('Content-type', 'text/csv')
        #        self.request.response.setHeader(
        #            'Content-Disposition', 'attachment; filename="db-items.csv"')
        #        out.seek(0)
        logger.info("CSV READY")


#        return out.getvalue()
#
# class ReindexMetadataScales(BrowserView):
#     def __call__(self):
#         catalog = api.portal.get_tool("portal_catalog")
#         column = self.request.form.get('column', 'image_scales')
#
#         # inverse = {}
#         # for p, rid in catalog._catalog.uids.items():
#         #     inverse[rid] = p
#
#         # passing an invalid index name gives all brains as a result
#         for brain in catalog.searchResults(missing_broken=True):
#             obj = brain.getObject()
#             pass
#
#         # this is a mapping path -> uid
#         for p in catalog._catalog.uids.keys():
#             catalog._catalog.updateMetadata()


class FindContentWithBlock(BrowserView):
    """Find the content that has a particular block"""

    def __call__(self):
        catalog = self.context.portal_catalog
        path = "/".join(self.context.getPhysicalPath())
        brains = catalog.searchResults(path=path, sort_on="path")
        block_type = self.request.form["type"]

        found = []
        for brain in brains:
            obj = brain.getObject()
            if not hasattr(obj.aq_inner.aq_self, "blocks"):
                continue
            types = set()
            bt = BlockType(obj, types)
            traverser = BlocksTraverser(obj)
            traverser(bt)
            if block_type in types:
                found.append(obj)

        return "\n".join([o.absolute_url() for o in found])
