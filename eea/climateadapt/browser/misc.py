import json
import logging
import re
import urllib
from email.MIMEText import MIMEText
from itertools import islice

import requests
import transaction
from BeautifulSoup import BeautifulSoup
from DateTime import DateTime
from dateutil.tz import gettz
from eea.climateadapt.config import CONTACT_MAIL_LIST
from eea.climateadapt.schema import Email
from OFS.ObjectManager import BeforeDeleteException
from plone import api
from plone.api import content, portal
from plone.api.content import get_state
from plone.api.portal import get_tool, show_message
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.widgets.dx import DatetimeWidgetConverter as BaseConverter
from plone.directives import form
from plone.formwidget.captcha.validator import (CaptchaValidator,
                                                WrongCaptchaCode)
from plone.formwidget.captcha.widget import CaptchaFieldWidget
from plone.memoize import view
from plone.z3cform.layout import wrap_form
from Products.CMFPlone.utils import getToolByName, isExpired
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button, field, validator
from ZODB.PersistentMapping import PersistentMapping
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.interface import Interface, implements

# from Acquisition import aq_inner
# from eea.climateadapt import MessageFactory as _

logger = logging.getLogger('eea.climateadapt')


class Captcha(object):
    subject = u""
    captcha = u""

    def __init__(self, context):
        self.context = context


class NewsletterRedirect(BrowserView):
    """ Redirect to newsletter #84251"""

    def __call__(self):
        return self.request.response.redirect('/newsletter')


class WebEmptyView(BrowserView):
    """ Empty view for /web #84251"""

    def __call__(self):
        return self.request.response.redirect('/newsletter')


class CalculateItemStatistics(BrowserView):
    """ Performs a catalog search for the portal types defined in the search()
        After visiting the view /calculate-item-statistics it initializes
        IAnnotations(site) -> performs the catalog search and saves the
        results to IAnnotations(site)

        'Total' refers to the number of total items, regardless of their review
        state (published/private/sent/pending/etc)
    """

    def __call__(self):
        return self.initialize()

    def initialize(self):
        self.initializeAnnotations()
        self.search()
        self.cleanUpData()

    def initializeAnnotations(self):
        """ Initializing Annotations """
        logger.info('Initializing Annotations')
        annot = IAnnotations(self.context)
        annot['cca-item-statistics'] = {}
        types = getToolByName(self.context, 'portal_types').listContentTypes()

        for year in range(1969, 2018):
            annotation = {}

            for ctype in types:
                annotation[ctype] = {'published': 0, 'total': 0}
            annot['cca-item-statistics'][year] = annotation
        logger.info("Finished Initializing Annotations")

    def search(self):
        """ Catalog search for all content types used """
        logger.info("Starting the catalog search")
        catalog = self.context.portal_catalog
        query = {'portal_type': [
                 'eea.climateadapt.aceproject',
                 'eea.climateadapt.tool',
                 'eea.climateadapt.researchproject',
                 'eea.climateadapt.publicationreport',
                 'eea.climateadapt.organisation',
                 'eea.climateadapt.city_profile',
                 'eea.climateadapt.mapgraphdataset',
                 'eea.climateadapt.informationportal',
                 'eea.climateadapt.indicator',
                 'eea.climateadapt.guidancedocument',
                 'eea.climateadapt.casestudy',
                 'eea.climateadapt.adaptationoption',
                 'Link',
                 'Document',
                 'News Item',
                 'Event',
                 'collective.cover.content',
                 'Folder',
                 'EasyForm',
                 'Collection']
                 }

        brains = catalog.searchResults(**query)
        logger.info('Got %s results.' % len(brains))
        items_count = 0

        for brain in brains:
            if items_count % 100 == 0:
                logger.info('Went through %s brains' % items_count)
            obj = brain.getObject()
            obj_state = api.content.get_state(obj)
            creation_year = obj.created().year()
            portal_type = obj.portal_type

            url = obj.absolute_url()

            if creation_year is None:
                logger.info("No creation date found for %s" % url)

                continue

            self.saveToAnnotations(creation_year, portal_type, False)

            if obj_state == 'published':
                publish_year = obj.effective().year()

                if publish_year is None:
                    logger.info("No publishing date found for %s" % url)

                    continue
                self.saveToAnnotations(publish_year, portal_type, True)
            items_count += 1
        logger.info('Finished the search.')

    def saveToAnnotations(self, year, content_type, published):
        """ Saves the number of brains depending on its review state """
        annotations = IAnnotations(self.context)['cca-item-statistics']

        if published:
            annotations[year][content_type]['published'] += 1
        annotations[year][content_type]['total'] += 1

    def cleanUpData(self):
        """ Cleans up all the unnecessary indexes """
        logger.info('Cleaning up DATA')

        for year in range(1969, 2018):
            annot = IAnnotations(self.context)
            annotation = annot['cca-item-statistics'][year]
            keys = annotation.keys()

            for key in keys:
                if annotation[key]['total'] == 0:
                    annotation.pop(key, None)
            keys = annotation.keys()

            if len(keys) == 0:
                IAnnotations(self.context)['cca-item-statistics'].pop(year)

                continue
        logger.info('Finished cleaning up data')


class getItemStatistics(BrowserView):
    """ BrowserView used in order to display the total number of brains present
        on the site in each year

        path: site/@@get-item-statistics
    """

    def __call__(self):
        return self.index()

    def get_portal_types(self, year):
        """ Filters out the portal types """
        all_types = [{xx[0]: xx[1].title}
                     for xx in self.context.portal_types.objectItems()]
        annotations = IAnnotations(self.context)['cca-item-statistics']

        types = []

        for pair in all_types:
            if pair.keys()[0] in annotations[year].keys():
                types.append(pair)

        return types

    def get_years(self):
        """ Gets the years present in IAnnotations and sorts them ascending """
        years = IAnnotations(self.context)['cca-item-statistics'].keys()
        years.sort()

        return years

    def get_published(self, year, portal_type):
        """ Gets the number of published items depending on year/portal_type"""
        annotations = IAnnotations(self.context)['cca-item-statistics']

        return annotations[year][portal_type]['published']

    def get_total(self, year, portal_type):
        """ Gets the number of total items depending on year/portal_type """
        annotations = IAnnotations(self.context)['cca-item-statistics']

        return annotations[year][portal_type]['total']


class FixCheckout(BrowserView):
    """ A view to fix getBaseline error when the original item was deleted
    and only the copy remains.
    """

    def __call__(self):
        policy = ICheckinCheckoutPolicy(self.context, None)
        relation = policy._get_relation_to_baseline()
        relation.from_object = relation.to_object
        relation._p_changed = True

        return "Fixed"


class ISimplifiedResourceRegistriesView(Interface):
    """ A view with simplified resource registries """


class TransRegionView(BrowserView):
    """ Custom view for /transnational-regions """

    implements(ISimplifiedResourceRegistriesView)


class CountriesView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/countries """

    implements(ISimplifiedResourceRegistriesView)


class MapViewerView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/tools/map-viewer """

    implements(ISimplifiedResourceRegistriesView)

    def __call__(self):
        return self.request.response.redirect('/tools/map-viewer?' +
                                              self.request['QUERY_STRING'])


class AdaptationStrategyView (BrowserView):
    """ Redirect for http://climate-adapt.eea.europa.eu/adaptation-strategies
        to /countries-view-map
    """

    @view.memoize
    def __call__(self):
        return self.request.response.redirect('/countries')


class RedirectToSearchView (BrowserView):
    """ Custom view for /content """

    def __init__(self, context, request):
        # Each view instance receives context and request as construction parameters
        self.context = context
        self.request = request

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')

        typeOfDataTo = self.request.other['ACTUAL_URL'].split('/')[-1]
        typeOfDataValues = {
            'adaptation-options':'Adaptation options',
            'case-studies':'Case studies',
            'indicators':'Indicators',
            'portals':'Information portals',
            'guidances':'Guidance',
            'organisations':'Organisations',
            'publications':'Publications and reports',
            'projects':'Research and knowledge projects',
            'tools':'Tools',
            'videos':'Videos',
            }

        navigation_root_url = portal_state.navigation_root_url()
        if '/observatory' in navigation_root_url:
            link = '/observatory/catalogue/'
        else:
            link = '/data-and-downloads/'

        if link == '/observatory/catalogue/' and typeOfDataTo == 'organisations':
            link = '/observatory/About/about-the-observatory#partners';
        else:
            querystring = self.request.form.get('SearchableText', "")
            query = {
                u'display_type': u'list',
                u'highlight': {
                  u'fields': {
                    u'*': {
                    }
                  }
                },
                u'query': {
                    u'bool': {
                        u'must':
                            [{u'term': {u'hasWorkflowState': u'published'}},
                             {u'query_string': {u'analyze_wildcard': True,
                                                u'default_operator': u'OR',
                                                u'query': querystring}
                             }]
                            }
                           }
                         }
            if typeOfDataTo in typeOfDataValues:
                query['query']['bool']['filter'] = {"bool":{"should":[{"term":{"typeOfData":typeOfDataValues[typeOfDataTo]}}]}}

            link = link + '?source=' + urllib.quote(json.dumps(query))

        return self.request.response.redirect(link)


class ExcelCsvExportView (BrowserView):
    """ View with links to the excel export for portal types """


class DetectBrokenLinksView (BrowserView):
    """ View for detecting broken links"""

    # def show_obj(self, path):
    #     """ Don't show objects which are not published
    #     """
    #     path = '/'.join(path)
    #     obj = self.context.restrictedTraverse(path)
    #     state = get_state(obj)
    #
    #     return state == 'published'

    def url(self, path):
        path = '/'.join(path[2:])
        return path

    def results(self):
        portal = api.portal.get()
        annot = IAnnotations(portal)['broken_links_data']
        latest_dates = sorted(annot.keys())[-5:]
        res = {}
        broken_links = []

        for date in latest_dates:
            for info in annot[date]:
                info = info.copy()
                try:
                    obj = self.context.restrictedTraverse(info['object_url'])
                except:
                    continue

                state = get_state(obj)
                if state not in ['private', 'archived']:
                    info['date'] = date.Date() if isinstance(
                        date, DateTime) else date
                    if (isinstance(date, str) and date=='pre_nov7_data'):
                        continue

                    broken_links.append(info)

        for link in broken_links:
            res[link['url']] = link

        return res


class ClearMacrotransnationalRegions (BrowserView):
    """ Clear the macrotransnational regions from geographic localization

    if all the regions are selected
    """

    def __call__(self):
        return
        logger.info('Starting to clear regions.')

        for brain in self.catalog_search():
            self.clear_regions(brain.getObject())
        logger.info('Finished clearing regions.')

    def catalog_search(self):
        catalog = self.context.portal_catalog
        query = {'portal_type': [
            'eea.climateadapt.aceproject',
            'eea.climateadapt.adaptationoption',
            'eea.climateadapt.casestudy',
            'eea.climateadapt.guidancedocument',
            'eea.climateadapt.indicator',
            'eea.climateadapt.informationportal',
            'eea.climateadapt.mapgraphdataset',
            'eea.climateadapt.organisation',
            'eea.climateadapt.publicationreport',
            'eea.climateadapt.researchproject',
            'eea.climateadapt.tool',
        ]}
        brains = catalog.searchResults(**query)

        return brains

    def clear_regions(self, obj):
        if obj.geochars in [None, u'', '', []]:
            return

        geochars = json.loads(obj.geochars)
        macro = geochars['geoElements'].get('macrotrans', [])

        if macro:
            if len(macro) == 13:
                logger.info('Clearing regions on %s' % obj.absolute_url())
                geochars['geoElements']['macrotrans'] = []
                geochars = json.dumps(geochars).encode()
                obj.geochars = geochars
                obj._p_changed = True
                obj.reindexObject()


class GetItemsForMacrotransRegions(BrowserView):
    """ Write to files the url of objects belonging to either the caribbean
    or se-europe region

    NOTE: this is one time use only view
    """

    def __call__(self):
        return

        for b in self.catalog_search():
            obj = b.getObject()

            if obj.geochars in [None, u'', '', []]:
                continue
            geochars = json.loads(obj.geochars)
            macro = geochars['geoElements'].get('macrotrans', [])

            if macro:
                if 'TRANS_MACRO_CAR_AREA' in macro:
                    self.write_caribbean(obj)

                if 'TRANS_MACRO_SE_EUR' in macro:
                    self.write_se_europe(obj)
        logger.info('Completed writing to files.')

    def write_caribbean(self, obj):
        logger.info('Writing %s to CARIBBEAN' % obj.absolute_url())
        with open('/'.join(['/tmp/', 'caribbean']), 'a') as f:
            f.writelines('Object URL: %s \n' % obj.absolute_url())

    def write_se_europe(self, obj):
        logger.info('Writing %s to SE EUROPE' % obj.absolute_url())
        with open('/'.join(['/tmp/', 'se-europe']), 'a') as f:
            f.writelines('Object URL: %s \n' % obj.absolute_url())

    def catalog_search(self):
        catalog = self.context.portal_catalog
        query = {
            'portal_type': [
                'eea.climateadapt.aceproject',
                'eea.climateadapt.adaptationoption',
                'eea.climateadapt.casestudy',
                'eea.climateadapt.guidancedocument',
                'eea.climateadapt.indicator',
                'eea.climateadapt.informationportal',
                'eea.climateadapt.mapgraphdataset',
                'eea.climateadapt.organisation',
                'eea.climateadapt.publicationreport',
                'eea.climateadapt.researchproject',
                'eea.climateadapt.tool',
            ]
        }
        brains = catalog.searchResults(**query)

        return brains


def _archive_news(site):
    """ Script that will get called by cron once per day
    """
    catalog = getToolByName(site, 'portal_catalog')
    query = {'portal_type': ['News Item', 'Link', 'Event'],
             'review_state': 'published'}
    brains = catalog.searchResults(**query)

    for b in brains:
        obj = b.getObject()
        # if isExpired(obj) == 1 and api.content.get_state(obj) != 'archived':

        if isExpired(obj) == 1:
            logger.info('Archiving %s' % obj.absolute_url())
            api.content.transition(obj, 'archive')
            transaction.commit()


def convert_to_string(item):
    """ Convert to string other types
    """

    if not item:
        return ''

    if not isinstance(item, basestring):
        new_item = ""
        try:
            iterator = iter(item)
        except TypeError, err:
            value = getattr(item, 'raw', None)

            if value:
                return value
            logger.error(err)

            return ''
        else:
            for i in iterator:
                new_item += i

        return new_item

    return item


def discover_links(string_to_search):
    """ Use regular expressions to get all urls in string
    """
    # REGEX = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.]
    # [a-z]{2,4}/)(?:[^\s()<>]|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>
    # ]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?\xab\xbb\u201c\u201d\u2018
    # \u2019]))')
    REGEX = re.compile(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    try:
        result = re.findall(REGEX, string_to_search) or []

        if isinstance(result, basestring):
            result = [result]
    except Exception, err:
        logger.error(err)
        result = []

    return result


def compute_broken_links(site):
    """ Script that will get called by cron once per day
    """

    results = []
    annot = IAnnotations(site)['broken_links_data']
    now = DateTime()
    links = get_links(site)

    if isinstance(annot, list):
        # store old data
        old_data = annot
        annot = PersistentMapping()
        IAnnotations(site)['broken_links_data'] = annot
        annot['pre_nov7_data'] = old_data

    for info in links:
        res = check_link(info['link'])
        if res is not None:
            res['object_url'] = info['object_url']
            results.append(res)

    annot[now] = results
    dates = annot.keys()

    if len(dates) >= 5:  # maximum no. of dates stored
        # delete oldest data except 'pre_nov7_data'
        del annot[sorted(dates)[0]]

    IAnnotations(site)._p_changed = True
    transaction.commit()


def get_links(site):
    """ Gets the links for all our items by using the websites field
        along with the respective object urls
    """

    catalog = getToolByName(site, 'portal_catalog')
    query = {
        'portal_type': [
            'eea.climateadapt.aceproject',
            'eea.climateadapt.adaptationoption',
            'eea.climateadapt.casestudy',
            'eea.climateadapt.guidancedocument',
            'eea.climateadapt.indicator',
            'eea.climateadapt.informationportal',
            'eea.climateadapt.mapgraphdataset',
            'eea.climateadapt.organisation',
            'eea.climateadapt.publicationreport',
            'eea.climateadapt.researchproject',
            'eea.climateadapt.tool',
            'eea.climateadapt.city_profile',
            'collective.cover.content',
        ]
    }
    brains = catalog.searchResults(**query)
    urls = []

    def append_urls(link, path): return urls.append({
        'link': link,
        'object_url': path
    })
    count = 0
    logger.info('Got %s objects' % len(brains))

    for b in brains:
        obj = b.getObject()
        path = obj.getPhysicalPath()

        if hasattr(obj, 'websites'):
            if isinstance(obj.websites, str):
                append_urls(obj.websites, path)
            else:
                for url in obj.websites:
                    append_urls(url, path)
        else:
            if obj.portal_type == 'eea.climateadapt.city_profile':
                append_urls(obj.website_of_the_local_authority, path)
        attrs = ['long_description', 'description', 'source', 'comments']

        for attr in attrs:
            string_to_search = convert_to_string(getattr(obj, attr, ''))

            if len(string_to_search) > 0:
                if attr == 'long_description':
                    bs = BeautifulSoup(string_to_search)
                    links = bs.findAll(
                        'a', attrs={'href': re.compile("^https?://")}
                    )

                    for link in links:
                        append_urls(link.get('href'), path)
                else:
                    links = discover_links(string_to_search)

                    # get rid of duplicates
                    links = list(set(links))

                    for link in links:
                        append_urls(link, path)

        if obj.portal_type == 'collective.cover.content':
            for tile in obj.list_tiles():
                if 'richtext' in obj.get_tile_type(tile):
                    richtext = obj.get_tile(tile).getText()
                    bs = BeautifulSoup(richtext)
                    links = bs.findAll(
                        'a', attrs={'href': re.compile("^https?://")}
                    )

                    for link in links:
                        append_urls(link.get('href'), path)

        count += 1

        if count % 100 == 0:
            logger.info('Finished going through %s objects' % count)

    logger.info("Finished getting links.")

    return urls


def check_link(link):
    """ Check the links and return only the broken ones with the respective
        status codes
    """

    if link:
        if isinstance(link, unicode):
            try:
                link = link.encode()
            except UnicodeEncodeError:
                logger.info('UnicodeEncodeError on link %s', link)

                return {'status': 504, 'url': link}

        try:
            if link[0:7].find('http') == -1:
                link = 'http://' + link
        except Exception, err:
            logger.error(err)

        logger.warning("Now checking: %s", link)

        try:
            requests.head(link, timeout=5, allow_redirects=True)
        except requests.exceptions.ReadTimeout:
            return {'status': '504', 'url': link}
        except requests.exceptions.ConnectTimeout:
            logger.info("Timed out.")
            logger.info("Trying again with link: %s", link)
            try:
                requests.head(link, timeout=30, allow_redirects=True)
            except:
                return {'status': '504', 'url': link}
        except requests.exceptions.TooManyRedirects:
            logger.info("Redirected.")
            logger.info("Trying again with link: %s", link)
            try:
                requests.head(link, timeout=30, allow_redirects=True)
            except:
                return {'status': '301', 'url': link}
        except requests.exceptions.URLRequired:
            return {'status': '400', 'url': link}
        except requests.exceptions.ProxyError:
            return {'status': '305', 'url': link}
        except requests.exceptions.HTTPError:
            return {'status': '505', 'url': link}
        except:
            return {'status': '404', 'url': link}

    return


class IContactForm(form.Schema):
    name = schema.TextLine(title=u"Name:", required=True)
    email = Email(title=u"Email:", required=True)
    feedback = schema.Choice(title=u"Type of feedback:", required=True,
                             values=[
                                 "Request for information",
                                 "Suggestion for Improvement",
                                 "Broken link",
                             ])
    message = schema.Text(title=u"Message:", required=True)

    captcha = schema.TextLine(
        title=u"Captcha",
        description=u"",
        required=False
    )


class ContactForm(form.SchemaForm):
    """ Contact Form
    """

    schema = IContactForm
    ignoreContext = True

    label = u"Contact CLIMATE-ADAPT"
    description = u""" Please use the contact form below if you have questions
    on CLIMATE-ADAPT, to suggest improvements for CLIMATE-ADAPT or to report
    broken links.
    """

    fields = field.Fields(IContactForm)
    fields['captcha'].widgetFactory = CaptchaFieldWidget

    @button.buttonAndHandler(u"Submit")
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return

        if 'captcha' in data:
            # Verify the user input against the captcha
            captcha = CaptchaValidator(self.context, self.request, None,
                                       IContactForm['captcha'], None)

            try:
                valid = captcha.validate(data['captcha'])
            except WrongCaptchaCode:
                show_message(message=u"Invalid Captcha.",
                             request=self.request, type='error')
                return

            if valid:
                mail_host = api.portal.get_tool(name='MailHost')
                # emailto = str(api.portal.getSite().email_from_address)

                mime_msg = MIMEText(data.get('message'))
                mime_msg['Subject'] = data.get('feedback')
                mime_msg['From'] = data.get('email')
                # mime_msg['To'] = ','.join(b for b in CONTACT_MAIL_LIST)
                # mime_msg['To'] = CONTACT_MAIL_LIST

                for m in CONTACT_MAIL_LIST:
                    mime_msg['To'] = m

                self.description = u"Email Sent."
                IStatusMessage(self.request).addStatusMessage(
                    "Email SENT",
                    'info')
                return mail_host.send(mime_msg.as_string())
            else:
                self.description = u"Please complete the Captcha."


class IContactFooterForm(form.Schema):

    name = schema.TextLine(title=u"Name:", required=True)
    email = Email(title=u"Your Email:", required=True)
    subject = schema.TextLine(title=u"Subject", required=True)
    message = schema.Text(title=u"Message:", required=True)

    captcha = schema.TextLine(
        title=u"Captcha",
        description=u"",
        required=False
    )


class ContactFooterForm(form.SchemaForm):
    """ Footer Contact Form
    """

    schema = IContactFooterForm
    ignoreContext = True

    label = u"Contact form"
    description = u""" Climate-ADAPT aims to support Europe in adapting to
    climate change. It is an initiative of the European Commission and helps
    users to access and share data and information on expected climate change
    in Europe. Fill in this form to contact the site owners.
    """

    fields = field.Fields(IContactFooterForm)
    fields['captcha'].widgetFactory = CaptchaFieldWidget

    @button.buttonAndHandler(u"Submit")
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return

        if 'captcha' in data:
            # Verify the user input against the captcha
            captcha = CaptchaValidator(self.context,
                                       self.request, None,
                                       IContactFooterForm['captcha'], None)

            try:
                valid = captcha.validate(data['captcha'])
            except WrongCaptchaCode:
                show_message(message=u"Invalid Captcha.",
                             request=self.request, type='error')
                return

            if valid:
                mail_host = api.portal.get_tool(name='MailHost')

                info = {'name': data.get('name'),
                        'mail': data.get('email'),
                        'url': self.context.absolute_url()}
                text = """

Climate Adapt Website

You are receiving this mail because %(name)s
%(mail)s
is sending feedback about the site you administer at %(url)s.
""" % info

            mime_msg = MIMEText(data.get('message') + text)
            mime_msg['Subject'] = data.get('subject')
            mime_msg['From'] = data.get('email')
            mime_msg['To'] = str(api.portal.getSite().email_from_address)

            self.description = u"Email Sent."

            IStatusMessage(self.request).addStatusMessage(
                "Email SENT",
                'info')

            return mail_host.send(mime_msg.as_string())
        else:
            self.description = u"Please complete the Captcha."


CaptchaForm = wrap_form(ContactForm)

# Register Captcha validator for the captcha field in the IContactForm
validator.WidgetValidatorDiscriminators(
    CaptchaValidator, field=IContactForm['captcha'])


CaptchaFooterForm = wrap_form(ContactFooterForm)

# Register Captcha validator for the captcha field in the IContactForm
validator.WidgetValidatorDiscriminators(
    CaptchaValidator, field=IContactFooterForm['captcha'])


def preventFolderDeletionEvent(object, event):
    for obj in object.listFolderContents():
        iterate_control = obj.restrictedTraverse('@@iterate_control')

        if iterate_control.is_checkout():
            # Cancel deletion
            raise BeforeDeleteException


class ViewGoogleAnalyticsReport(BrowserView):
    """ A view to view the google analytics report data
    """

    def report_data(self):

        site = portal.get()
        report = site.__annotations__.get('google-analytics-cache-data', {})

        reports = reversed(sorted(report.items(), key=lambda x: int(x[1])))

        return islice(reports, 0, 10)


class DatetimeDataConverter(BaseConverter):
    """ Avoid problem with missing tzinfo from default datetime widgets
    """

    def toFieldValue(self, value):
        logger.warn('dateconvertwidget', value)
        value = super(DatetimeDataConverter, self).toFieldValue(value)
        if value is not self.field.missing_value:
            if not getattr(value, 'tzinfo', None):
                value = value.replace(tzinfo=gettz())
        return value


class C3sIndicatorsOverview(BrowserView):
    """ Overview page for indicators. Registered as @@c3s_indicators_overview

    To be used from inside a collective.cover
    """

    @property
    def indicators(self):
        brains = content.find(portal_type='eea.climateadapt.c3sindicator')
        return [b.getObject() for b in brains]

    def json_indicator_page_to_url(self, json_indicator_page):
        """ Given an indicator html page URL, it resolves to an imported indicator
        """
        html_page = json_indicator_page.split('/')[-1]
        for iid, info in self.data.get('indicators', {}).items():
            if info['overviewpage'] == html_page:
                for indicator in self.indicators:
                    if indicator.c3s_identifier == info['identifier']:
                        return indicator.absolute_url()

    @property
    def data(self):
        site = portal.get()
        base_folder = site["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get('c3s_json_data', {})
        return datastore.get('data', {})

    def get_categories(self):
        site = portal.get()
        base_folder = site["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get('c3s_json_data', {})
        data_overview_page = datastore['data']['overview_page']

        response = []
        #hazard_type_order = data_overview_page['hazard_type_order']
        hazard_type_order = data_overview_page['hazard_type_order_left'] + data_overview_page['hazard_type_order_right']
        #hazard_type_order.append(['Other'])

        for index, main_category in enumerate(data_overview_page['category_order']):
            if main_category in data_overview_page['hazard_list']:
                category_data = data_overview_page['hazard_list'][main_category]

                subcategories = hazard_type_order[index]
                res = []
                for subcategory in subcategories:
                    if subcategory in category_data:
                        res.append((subcategory, category_data[subcategory]))
                response.append({
                    'name': main_category,
                    'data': res
                    })

        return response

    def get_disclaimer(self):
        site = portal.get()
        base_folder = site["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get('c3s_json_data', {})
        return datastore['data']['html_pages']['disclaimer']['page_text']

    def __call__(self):
        return self.index()
