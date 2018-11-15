import datetime
import json
import logging

from collective.cover.tiles.list import ListTile
from zope import schema
from zope.component import adapter, getMultiAdapter, getUtility
from zope.interface import (Interface, Invalid, implementer, implements,
                            invariant)

from apiclient.discovery import build
from eea.climateadapt.browser.site import _extract_menu
from eea.climateadapt.interfaces import IGoogleAnalyticsAPI
from eea.climateadapt.scripts import get_plone_site
from oauth2client.service_account import ServiceAccountCredentials
from plone.api import portal
from plone.api.portal import get_tool
from plone.app.registry.browser.controlpanel import (ControlPanelFormWrapper,
                                                     RegistryEditForm)
from plone.app.widgets.dx import RelatedItemsWidget
from plone.app.widgets.interfaces import IWidgetsLayer
from plone.directives import form
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from z3c.form import form as z3cform
from z3c.form import button
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList

logger = logging.getLogger('eea.climateadapt')


class CheckCopyPasteLocation(BrowserView):
    """ Performs a check which doesn't allow user to Copy cca-items
        if they belong to the group extranet-cca-editors
    """

    def __call__(self, action, object):
        return self.check(action, object)

    @view.memoize
    def check(self, action, object):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state")
        user = portal_state.member().getUser().getId()
        groups = getToolByName(self, 'portal_groups').getGroupsByUserId(user)

        for group in groups:
            if group.id == 'extranet-cca-editors' and 'metadata' in \
                    self.context.getPhysicalPath():

                logger.info("Can't Copy: returning False")

                return False

        return True


class InvalidMenuConfiguration(Invalid):
    __doc__ = u"The menu format is invalid"


class IMainNavigationMenu(form.Schema):
    menu = schema.Text(title=u"Menu structure text", required=True)

    @invariant
    def check_menu(data):
        try:
            _extract_menu(data.menu)
        except Exception, e:
            raise InvalidMenuConfiguration(e)


class MainNavigationMenuEdit(form.SchemaForm):
    """ A page to edit the main site navigation menu
    """

    schema = IMainNavigationMenu
    ignoreContext = False

    label = u"Fill in the content of the main menu"
    description = u"""This should be a structure for the main menu. Use a single
    empty line to separate main menu entries. All lines after the main menu
    entry, and before an empty line, will form entries in that section menu. To
    create a submenu for a section, start a line with a dash (-).  Links should
    start with a slash (/)."""

    @property
    def ptool(self):
        return getToolByName(self.context,
                             'portal_properties')['site_properties']

    @view.memoize
    def getContent(self):
        content = {'menu': self.ptool.getProperty('main_navigation_menu')}

        return content

    @button.buttonAndHandler(u"Save")
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return

        self.ptool._updateProperty('main_navigation_menu', data['menu'])

        self.status = u"Saved, please check."


class ForceUnlock(BrowserView):
    """ Forcefully unlock a content item
    """

    def __call__(self):
        annot = getattr(self.context, '__annotations__', {})

        if hasattr(self.context, '_dav_writelocks'):
            del self.context._dav_writelocks
            self.context._p_changed = True

        if 'plone.locking' in annot:
            del annot['plone.locking']

            self.context._p_changed = True
            annot._p_changed = True

        url = self.context.absolute_url()
        props_tool = getToolByName(self.context, 'portal_properties')

        if props_tool:
            types_use_view = \
                props_tool.site_properties.typesUseViewActionInListings

            if self.context.portal_type in types_use_view:
                url += '/view'

        return self.request.RESPONSE.redirect(url)


class ListTilesWithTitleView (BrowserView):
    """ View that lists all tiles with richtext title and their respective urls
    """

    def __call__(self):
        covers = self.context.portal_catalog.searchResults(
                              portal_type='collective.cover.content')
        self.urls = []

        for cover in covers:
            cover = cover.getObject()

            self.tiles = []

            self.walk(json.loads(cover.cover_layout))

            if hasattr(cover, '__annotations__'):
                for tile_id in self.tiles:
                    tile_id = tile_id.encode()
                    self.urls.append(cover.absolute_url())

        return self.index()

    @view.memoize
    def linkify(self, text):
        if not text:
            return

        if text.startswith('/') or text.startswith('http'):
            return text

        return "http://" + text

    def walk(self, item):
        if isinstance(item, dict):
            if item.get('tile-type') == 'eea.climateadapt.richtext_with_title':
                self.tiles.append(item['id'])

            self.walk(item.get('children', []))
        elif isinstance(item, list):
            for x in item:
                self.walk(x)


class SpecialTagsInterface(Interface):
    """ Marker interface for /tags-admin """


class SpecialTagsView(BrowserView):
    """ Custom view for administration of special tags
    """
    implements(SpecialTagsInterface)

    def __call__(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state")

        action = self.request.form.get('action', None)
        tag = self.request.form.get('tag', None)

        if portal_state.anonymous():
            return self.index()

        if action:
            getattr(self, 'handle_' + action)(tag)

        return self.index()

    @view.memoize
    def special_tags(self):
        return self.context.portal_catalog.uniqueValuesFor('special_tags')

    def get_tag_length(self, tag):
        catalog = self.context.portal_catalog._catalog

        return len(catalog.indexes['special_tags']._index[tag])

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
                        key for key in obj.special_tags if key != tag)
                obj.reindexObject()
                obj._p_changed = True
        logger.info("Deleted tag: %s", tag)

    def handle_add(self, tag):
        pass

    def handle_rename(self, tag):
        catalog = self.context.portal_catalog
        newtag = self.request.form.get('newtag', None)

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
                        key for key in obj.special_tags if key != tag)
                    obj.special_tags += (newtag, )
                obj._p_changed = True
                obj.reindexObject()
        logger.info("Finished renaming: %s TO %s", tag, newtag)


class SpecialTagsObjects (BrowserView):
    """ Gets the links for the special tags that we get in the request
    """

    def __call__(self):
        tag = self.request.form['special_tags'].decode('utf-8')
        tag_obj = [b.getURL() + '/edit' for b in
                   self.context.portal_catalog.searchResults(special_tags=tag)]

        return json.dumps(tag_obj)


class IAddKeywordForm(form.Schema):
    keyword = schema.TextLine(title=u"Keyword:", required=True)
    ccaitems = RelationList(
        title=u"Select where to implement the new keyword",
        default=[],
        description=(u"Items related to the keyword:"),
        value_type=RelationChoice(
            title=(u"Related"),
            vocabulary="eea.climateadapt.cca_items"
        ),
        required=False,
    )


class AddKeywordForm (form.SchemaForm):
    schema = IAddKeywordForm
    ignoreContext = True

    label = u"Add keyword"
    description = u""" Enter the new keyword you want to add """

    @button.buttonAndHandler(u"Submit")
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return

        keyword = data.get('keyword', None)
        objects = data.get('ccaitems', [])

        if keyword:
            for obj in objects:
                if isinstance(obj.keywords, (list, tuple)):
                    obj.keywords = list(obj.keywords)
                    obj.keywords.append(keyword)
                    obj._p_changed = True
                    obj.reindexObject()
            self.status = "Keyword added"

            return self.status


@adapter(getSpecification(IAddKeywordForm['ccaitems']), IWidgetsLayer)
@implementer(IFieldWidget)
def CcaItemsFieldWidget(field, request):
    """ The vocabulary view is overridden so that
        the widget will show all cca items
        Check browser/overrides.py for more details
    """
    widget = FieldWidget(field, RelatedItemsWidget(request))
    widget.vocabulary = 'eea.climateadapt.cca_items'
    widget.vocabulary_override = True

    return widget


class KeywordsAdminView (BrowserView):
    """ Custom view for the administration of keywords
    """

    def __call__(self):
        action = self.request.form.get('action', None)
        keyword = self.request.form.get('keyword', None)

        if action:
            getattr(self, 'handle_' + action)(keyword)

        return self.index()

    @view.memoize
    def keywords(self):
        return self.context.portal_catalog.uniqueValuesFor('keywords')

    def get_keyword_length(self, key):
        catalog = self.context.portal_catalog._catalog

        return len(catalog.indexes['keywords']._index[key])

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

    def handle_rename(self, keyword):
        catalog = self.context.portal_catalog
        newkeyword = self.request.form.get('newkeyword', None)

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
                    obj.keywords += (newkeyword, )
                obj._p_changed = True
                obj.reindexObject()
        logger.info("Finished renaming: %s TO %s", keyword, newkeyword)


class KeywordObjects (BrowserView):
    """ Gets the links for the keyword that we get in the request
    """

    def __call__(self):
        key = self.request.form['keyword'].decode('utf-8')
        key_obj = [b.getURL() + '/edit' for b in
                   self.context.portal_catalog.searchResults(keywords=key)]

        return json.dumps(key_obj)


class GoogleAnalyticsAPIEditForm(RegistryEditForm):
    """
    Define form logic
    """

    z3cform.extends(RegistryEditForm)
    schema = IGoogleAnalyticsAPI


ConfigureGoogleAnalyticsAPI = layout.wrap_form(
    GoogleAnalyticsAPIEditForm, ControlPanelFormWrapper)

ConfigureGoogleAnalyticsAPI.label = u"Setup Google Analytics API Integration"


def initialize_analyticsreporting(credentials_data):
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
    An authorized Analytics Reporting API V4 service object.
    """
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    # json_data = json.loads(open(KEY_FILE_LOCATION).read())
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_data, SCOPES)

    # Build the service object.

    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def custom_report(analytics, view_id):
    now = datetime.datetime.now()

    return analytics.reports().batchGet(
        body={"reportRequests": [
            {
                "viewId": view_id,
                "dateRanges": [
                    {
                        "startDate": "2018-04-13",
                        "endDate": now.strftime("%Y-%m-%d")
                    }
                ],
                "metrics": [
                    {
                        "expression": "ga:totalEvents"
                    }
                ],
                "dimensions": [
                    {
                        "name": "ga:eventLabel"
                    }
                ],
                "pivots": [
                    {
                        "dimensions": [
                            {
                                "name": "ga:sessionCount"
                            }
                        ],
                        "metrics": [
                            {
                                "expression": "ga:users"
                            }
                        ]
                    }
                ],
                "orderBys": [
                    {
                        "fieldName": "ga:totalEvents",
                        "sortOrder": "DESCENDING"
                    }
                ],
                "dimensionFilterClauses": [
                    {
                        "filters": [
                            {
                                "dimensionName": "ga:eventCategory",
                                "expressions": [
                                    "database-search"
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
              }
    ).execute()


def parse_response(response):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
    response: An Analytics Reporting API V4 response.
    """

    result = {}
    reports = response.get('reports', [])

    if not reports:
        return result

    report = reports[0]

    for row in report.get('data', {}).get('rows', []):
        label = row['dimensions'][0]

        # value = row['metrics'][0]['pivotValueRegions'][0]['values'][0]
        value = row['metrics'][0]['values'][0]

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

    site.__annotations__['google-analytics-cache-data'] = res
    site.__annotations__._p_changed = True

    import transaction
    transaction.commit()

    return res


def refresh_analytics_data(site=None):
    if site is None:
        site = get_plone_site()
    _refresh_analytics_data(site)


class RefreshGoogleAnalyticsReport(BrowserView):
    """ A view to manually refresh google analytics report data
    """

    def __call__(self):

        site = portal.get()

        return refresh_analytics_data(site)


class ViewGoogleAnalyticsReport(BrowserView):
    """ A view to view the google analytics report data
    """

    def __call__(self):

        site = portal.get()

        return str(site.__annotations__.get('google-analytics-cache-data', {}))


class GoPDB(BrowserView):
    def __call__(self):
        import pdb
        pdb.set_trace()


class MigrateTiles(BrowserView):

    def process(self, cover):
        tileids = cover.list_tiles(
            types=['eea.climateadapt.relevant_acecontent']
        )

        for tid in tileids:
            tile = cover.get_tile(tid)

            if not tile.assigned():
                brains = tile.items()
                uids = [b.UID for b in brains]

                if uids:
                    tile.populate_with_uuids(uids)

                    data_mgr = ITileDataManager(tile)
                    old_data = data_mgr.get()
                    old_data['sortBy'] = 'NAME'
                    data_mgr.set(old_data)

                    print("Fixed cover %s, tile %s with uids %r" % (
                                cover.absolute_url(),
                                tid,
                                uids,
                                ))

                    logger.info("Fixed cover %s, tile %s with uids %r",
                                cover.absolute_url(),
                                tid,
                                uids,
                                )

    def __call__(self):
        catalog = get_tool('portal_catalog')
        brains = catalog(portal_type='collective.cover.content')

        for brain in brains:
            obj = brain.getObject()
            self.process(obj)

        return 'done'
