# -*- coding: utf-8 -*-
import datetime
import json
import logging

from lxml.etree import fromstring
from pkg_resources import resource_filename
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter, getMultiAdapter, getUtility
from zope.interface import (Interface, Invalid, implementer, implements,
                            invariant)

from apiclient.discovery import build
from DateTime import DateTime
from eea.climateadapt.browser.site import _extract_menu
from eea.climateadapt.interfaces import IGoogleAnalyticsAPI
from eea.climateadapt.scripts import get_plone_site
from eea.rdfmarshaller.actions.pingcr import ping_CRSDS
from oauth2client.service_account import ServiceAccountCredentials
from plone.api import portal
from plone.api.portal import get_tool, getSite
from plone.app.registry.browser.controlpanel import (ControlPanelFormWrapper,
                                                     RegistryEditForm)
from plone.app.widgets.dx import RelatedItemsWidget
from plone.app.widgets.interfaces import IWidgetsLayer
from plone.directives import form
from plone.i18n.normalizer import idnormalizer
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from six.moves.html_parser import HTMLParser
from z3c.form import form as z3cform
from z3c.form import button
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList

from plone.app.layout.navigation.navtree import buildFolderTree
from Products.CMFPlone.browser.navtree import DefaultNavtreeStrategy
from plone.app.layout.navigation.navtree import NavtreeStrategyBase
from plone import api

html_unescape = HTMLParser().unescape

logger = logging.getLogger('eea.climateadapt')


from plone.api import content
from plone.app.multilingual.factory import DefaultTranslationFactory
from plone.app.multilingual.manager import TranslationManager
from eea.climateadapt.tiles.richtext import RichTextWithTitle
from eea.climateadapt.translation import retrieve_translation
from collective.cover.tiles.richtext import RichTextTile
import transaction
import json

from datetime import date
from DateTime import DateTime
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage, NamedBlobFile, NamedFile, NamedImage
from zope.schema import getFieldsInOrder
from plone.behavior.interfaces import IBehaviorAssignable
from plone.formwidget.geolocation.geolocation import Geolocation
from z3c.relationfield.relation import RelationValue


def is_json(input):
    try:
        json.loads(input)
    except ValueError as e:
        return False
    return True


def force_unlock(context):
    annot = getattr(context, '__annotations__', {})

    if hasattr(context, '_dav_writelocks'):
        del context._dav_writelocks
        context._p_changed = True

    if 'plone.locking' in annot:
        del annot['plone.locking']

        context._p_changed = True
        annot._p_changed = True


def translate_obj(obj):
    tile_fields = ['title', 'description', 'tile_title', 'footer', 'alt_text']
    errors = []
    force_unlock(obj)

    # get behavior fields and values
    behavior_assignable = IBehaviorAssignable(obj)
    fields = {}
    if behavior_assignable:
        behaviors = behavior_assignable.enumerateBehaviors()
        for behavior in behaviors:
            for k,v in getFieldsInOrder(behavior.interface):
                fields.update({k: v})

    #  get schema fields and values
    for k, v in getFieldsInOrder(obj.getTypeInfo().lookupSchema()):
        fields.update({k: v})

    translations = TranslationManager(obj).get_translations()
    translations.pop('en')
    for language in translations:
        trans_obj = translations[language]

        # get tile data
        if trans_obj.portal_type == 'collective.cover.content':
            tiles_id = trans_obj.list_tiles()

            for tile_id in tiles_id:
                tile = trans_obj.get_tile(tile_id)
                for field in tile_fields:
                    value = tile.data.get(field)
                    if value:
                        translated = retrieve_translation('EN', value, [language.upper()])

                        if 'translated' in translated:
                            encoded_text = translated['transId'].encode('latin-1')
                            tile.data.update({field: encoded_text})

                if isinstance(tile, RichTextWithTitle) or \
                   isinstance(tile, RichTextTile):
                    try:
                        value = tile.data.get('text').raw
                    except Exception:
                        value = None
                    if value:
                        translated = retrieve_translation('EN', value, [language.upper()])
                        if 'translated' in translated:
                            try:
                                encoded_text = translated['transId'].encode('latin-1')
                                tile.data['text'].raw = encoded_text
                            except AttributeError:
                                logger.info("Error for tile. TODO improve.")
                                logger.info(tile_id)

        # send requests to translation service for each field
        # update field in obj
        for key in fields:
            rich = False
            print key
            if key in ['acronym', 'id', 'language', 'portal_type', 'contentType']:
                continue

            value = getattr(getattr(obj, key), 'raw', getattr(obj, key))

            if trans_obj.portal_type == 'Event':
                force_unlock(trans_obj)
                reindex = False
                if key == 'start':
                    # setattr(trans_obj, key, obj.start)
                    trans_obj.start = obj.start
                    reindex = True
                if key == 'end':
                    trans_obj.end = obj.end
                    # setattr(trans_obj, key, obj.start)
                    reindex = True
                if key == 'effective':
                    trans_obj.setEffectiveDate(obj.effective_date)
                    reindex = True
                if key == 'timezone':
                    trans_obj.timezone = obj.timezone
                    reindex = True

                if reindex is True:
                    # reindex object
                    trans_obj._p_changed = True
                    trans_obj.reindexObject()
                    continue

                    # transaction.commit()

            if not value:
                continue

            if callable(value):
                # ignore datetimes
                if isinstance(value(), DateTime):
                    continue

                value = value()

            # ignore some value types
            if isinstance(value, bool) or \
               isinstance(value, int) or \
               isinstance(value, long) or \
               isinstance(value, tuple) or \
               isinstance(value, list) or \
               isinstance(value, set) or \
               isinstance(value, dict) or \
               isinstance(value, NamedBlobImage) or \
               isinstance(value, NamedBlobFile) or \
               isinstance(value, NamedImage) or \
               isinstance(value, NamedFile) or \
               isinstance(value, DateTime) or \
               isinstance(value, date) or \
               isinstance(value, RelationValue) or \
               isinstance(value, Geolocation):
                continue

            if isinstance(getattr(obj, key), RichTextValue)
                value = getattr(obj, key).output
                rich = True

            if is_json(value):
                continue

            if key not in errors:
                errors.append(key)
            force_unlock(trans_obj)
            translated = retrieve_translation('EN', value, [language.upper()])
            if 'translated' in translated:
                encoded_text = translated['transId'].encode('latin-1')
                if rich:
                    setattr(getattr(trans_obj, key), 'raw', encoded_text)
                else:
                    setattr(trans_obj, key, encoded_text)

                # reindex object
                trans_obj._p_changed = True
                trans_obj.reindexObject(idxs=[key])

        return {'errors': errors}

def initiate_translations(site):
    catalog = site.portal_catalog
    count = 0
    res = catalog.searchResults(path='/cca/en')
    errors = []

    for brain in res:
        if brain.getPath() == '/cca/en' or brain.portal_type in ['LIF', 'LRF']:
            continue

        obj = brain.getObject()
        try:
            result = translate_obj(obj)
        except Exception as err:
            logger.info(err)
            # errors.append(err)
            # import pdb; pdb.set_trace()

        if len(result['errors']) > 0:
            for error in result['errors']:
                errors.append(error)

        count += 1
        if count % 100 == 0:
            logger.info("Processed %s objects" % count)
            transaction.commit()
    logger.info("DONE")
    logger.info(errors)

def get_tile_type(tile, from_cover, to_cover):
    tiles_types = {
        'RichTextWithTitle': 'eea.climateadapt.richtext_with_title',
        'EmbedTile': 'collective.cover.embed',
        'RichTextTile': 'collective.cover.richtext',
        'SearchAceContentTile': 'eea.climateadapt.search_acecontent',
        'GenericViewTile': 'eea.climateadapt.genericview',
        'RelevantAceContentItemsTile': 'eea.climateadapt.relevant_acecontent',
        'ASTNavigationTile': 'eea.climateadapt.ast_navigation',
        'ASTHeaderTile': 'eea.climateadapt.ast_header',
        'FilterAceContentItemsTile': 'eea.climateadapt.filter_acecontent',
        'TransRegionalSelectTile': 'eea.climateadapt.transregionselect',
        'SectionNavTile': 'eea.climateadapt.section_nav',
        'CountrySelectTile': 'eea.climateadapt.countryselect',
        'BannerTile': 'collective.cover.banner',
        'ShareInfoTile': 'eea.climateadapt.shareinfo',
        'FormTile': 'eea.climateadapt.formtile',
        'UrbanMenuTile': 'eea.climateadapt.urbanmenu',
        'CardsTile': 'eea.climateadapt.cards_tile',
    }
    for a_type in tiles_types.keys():
        if a_type in str(type(tile)):
            return tiles_types[a_type]

    return None

def copy_tiles(tiles, from_cover, to_cover):
    logger.info("Copy tiles")
    logger.info(from_cover.absolute_url())
    logger.info(to_cover.absolute_url())
    for tile in tiles:
        tile_type = get_tile_type(tile, from_cover, to_cover)

        if tile_type is not None:
            from_tile = from_cover.restrictedTraverse(
                '@@{0}/{1}'.format(tile_type, tile.id)
            )

            to_tile = to_cover.restrictedTraverse(
                '@@{0}/{1}'.format(tile_type, tile.id)
            )

            from_data_mgr = ITileDataManager(from_tile)
            to_data_mgr = ITileDataManager(to_tile)
            to_data_mgr.set(from_data_mgr.get())

        else:
            logger.info("Missing tile type")


def create_translation_object(obj, language):
    factory = DefaultTranslationFactory(obj)

    translated_object = factory(language)

    TranslationManager(obj).register_translation(language, translated_object)
    translated_object.reindexObject()

    if obj.portal_type == 'collective.cover.content':
        tiles = [obj.get_tile(x) for x in obj.list_tiles()]
        translated_object.cover_layout = obj.cover_layout
        copy_tiles(tiles, obj, translated_object)

        translated_object.reindexObject()


def get_all_objs(container):
    all_objs = []

    def get_objs(context):
        contents = api.content.find(context=context, depth=1)
        for item in contents:
            all_objs.append(item)

        for item in contents:
            get_objs(item.getObject())

    get_objs(container)

    return all_objs


def execute_trans_script(site, language):
    catalog = site.portal_catalog
    english_container = site['en']
    language_folders = [x.id for x in catalog.searchResults(path='/cca', portal_type='LRF')]
    language_folders.remove('en')

    lang_independent_objects = [
        "newsletter", "Members", "repository", "test-baltic", "frontpage",
        "admin",  "more-latest-updates", "sandbox", "portal_pdf",
        "portal_vocabularies", "portal_depiction", "frontpage-slides",
        "dashboard", "latest-modifications-on-climate-adapt",
        "covenant-of-mayors-external-website", "rss-feed",
        "latest-news-events-on-climate-adapt", "specific-privacy-statement-for-climate-adapt",
        "privacy-and-legal-notice", "database-items-overview", "broken-links",
        "observatory-organisations", "observatory-management-group-organisations",
        "indicators-backup", "eea-copyright-notice", "eea-disclaimer", "user-dashboard"]

    # move folders under /en/
    for brain in site.getFolderContents():
        obj = brain.getObject()

        if obj.portal_type != 'LRF' and obj.id not in lang_independent_objects:
            content.move(source=obj, target=english_container)

    transaction.commit()
    errors = []
    # get and parse all objects under /en/
    res = get_all_objs(english_container)

    failed_translations = []
    for brain in res:
        if brain.getPath() == '/cca/en' or brain.portal_type == 'LIF':
            continue
        obj = brain.getObject()
        try:
            create_translation_object(obj, language)
            logger.info("Cloned: %s" % obj.absolute_url())
        except Exception as err:
            errors.append(obj)
            logger.info("Error cloning: %s" % obj.absolute_url())
            continue
    transaction.commit()
    logger.info("Errors")
    logger.info(errors)
    logger.info("Finished cloning for language %s" % language)

    return 'Finished cloning for language %s' % language


class PrepareTranslation(BrowserView):
    """ Clone the content to be available for a new translation
        Usage: /admin-prepare-translation?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        from zope.site.hooks import getSite
        return execute_trans_script(getSite(), **kwargs)


class RunTranslation(BrowserView):
    """ Translate the contents
        Usage: /admin-run-translation
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        from zope.site.hooks import getSite
        return initiate_translations(getSite())

class RunTranslationSingleItem(BrowserView):
    """ Translate a single item
        Usage: item/admin-translate-this

        To be used for testing translation without waiting for all objects to be updated
    """

    def __call__(self, **kwargs):
        obj = self.context
        result = translate_obj(obj)
        transaction.commit()
        return result

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
            if not group:
                continue
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


class HealthNavigationMenuEdit(form.SchemaForm):
    """ A page to edit the main site navigation menu
    """

    schema = IMainNavigationMenu
    ignoreContext = False

    label = u"Fill in the content of the health navigation menu"
    description = u"""This should be a structure for health menu. Use a single
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
        content = {'menu': self.ptool.getProperty('health_navigation_menu')}

        return content

    @button.buttonAndHandler(u"Save")
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return

        self.ptool._updateProperty('health_navigation_menu', data['menu'])

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


class ForcePingCRView(BrowserView):
    """ Force pingcr on objects between a set interval """

    def __call__(self):
        cat = get_tool('portal_catalog')

        query = {
            'review_state': ['published', 'archived', 'private']
        }
        results = cat.searchResults(query)

        logger.info("Found %s objects " % len(results))

        count = 0
        options = {}
        options['create'] = False
        options['service_to_ping'] = 'http://semantic.eea.europa.eu/ping'
        for res in results:
            context = res.getObject()
            url = res.getURL()

            if 'https' in url:
                url = url.replace('https', 'http')

            options['obj_url'] = url + '/@@rdf'
            logger.info("Pinging: %s", url)
            ping_CRSDS(context, options)
            logger.info("Finished pinging: %s", url)

            count += 1
            if count % 100 == 0:
                logger.info('Went through %s brains' % count)

        logger.info('Finished pinging all brains')
        return 'Finished'


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


class Item:
    def __init__(self, node):
        self._node = node

    def __getattr__(self, name):
        org_name = name
        name = 'field_' + name
        field = self._node.find(name)

        if field is not None:
            return field.text
        if org_name in ['item_id', 'item_changed']:
            field = self._node.find(org_name)
            return field.text
        if org_name in ['sectors', 'keywords', 'impact', 'websites']:
            return ''
        if org_name in ['governance', 'websites']:
            return []
        if org_name in ['regions']:
            return {"geoElements": {"element": "EUROPE", "biotrans": []}}
        return None


class AdapteCCACurrentCaseStudyFixImportIDs(BrowserView):
    """ AdapteCCA current case study fix import ids
    """

    def __call__(self):
        fpath = resource_filename('eea.climateadapt.browser',
                                  'data/cases_en_cdata.xml')

        s = open(fpath).read()
        e = fromstring(s)
        container = getSite()['metadata']['case-studies']

        for item_node in e.xpath('//item'):
            item_id, field_title = '', ''
            for child in item_node.iterchildren():
                if child.tag == 'item_id':
                    item_id = child.text
                if child.tag == 'field_title':
                    field_title = idnormalizer.normalize(child.text, None, 500)

            if item_id and field_title:
                annot = IAnnotations(container[field_title])
                annot['import_id'] = item_id

        return 'AdapteCCA current case study fixed import_ids'


class ConvertPythonDatetime(BrowserView):
    """ Convert effective_date and creation_date from python datetime to
    DateTime
    """

    def __call__(self):

        brains = self.context.portal_catalog.searchResults(wrong_index=True)
        for brain in brains:
            obj = brain.getObject()
            obj = obj.aq_inner.aq_self
            for name in ['creation_date', 'effective_date']:
                attr = getattr(obj, name, None)
                if isinstance(attr, datetime.datetime):
                    setattr(obj, name, DateTime(attr))
                    logger.info("Fix %s: %s - %s", brain.getURL(), name, attr)

        return "done"
