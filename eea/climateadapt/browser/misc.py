import json
import logging
import re
import requests
import transaction

from Acquisition import aq_inner
from BeautifulSoup import BeautifulSoup
from eea.climateadapt.config import CONTACT_MAIL_LIST
from eea.climateadapt.schema import Email
from email.MIMEText import MIMEText
from itertools import islice
from OFS.ObjectManager import BeforeDeleteException
from plone import api
from plone.api import portal
from plone.api.content import get_state
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.directives import form
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget
from plone.memoize import view
from Products.CMFPlone.utils import getToolByName, isExpired
from Products.Five.browser import BrowserView
from z3c.form import button, field
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.interface import Interface, implements


logger = logging.getLogger('eea.climateadapt')


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

    def __call__(self):
        type_name = self.context.getProperty('search_type_name', '')
        url = '/data-and-downloads'

        if type_name:
            url += '#searchtype=' + type_name

        return self.request.response.redirect(url)


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
        annot = IAnnotations(self.context)
        res = []
        for info in annot.get('broken_links_data', []):
            obj = self.context.restrictedTraverse(info['object_url'])
            state = get_state(obj)

            if state not in ['private', 'archived']:
                res.append(info)

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


def compute_broken_links(site):
    """ Script that will get called by cron once per day
    """
    links = get_links(site)

    results = []

    for info in links:
        res = check_link(info['link'])

        if res is not None:
            res['object_url'] = info['object_url']
            results.append(res)

    IAnnotations(site)['broken_links_data'] = results
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

    append_urls = lambda link, path: urls.append({
        'link': link,
        'object_url': path
    })

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

            elif obj.portal_type == 'collective.cover.content':
                for tile in obj.list_tiles():
                    if 'richtext' in obj.get_tile_type(tile):
                        richtext = obj.get_tile(tile).getText()
                        bs = BeautifulSoup(richtext)
                        links = bs.findAll(
                            'a', attrs={'href': re.compile("^https?://")}
                        )
                        for link in links:
                            append_urls(link.get('href'), path)
            else:
                logger.info("Portal type: %s" % obj.portal_type)

    logger.info("Finished getting links.")

    return urls


def check_link(link):
    """ Check the links and return only the broken ones with the respective
        status codes
    """

    if link:
        if isinstance(link, unicode):
            link = link.encode()

        if link[0:7].find('http') == -1:
            link = 'http://' + link

        logger.info("LINK: %s", link)
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
        title=u"ReCaptcha",
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
    fields['captcha'].widgetFactory = ReCaptchaFieldWidget

    @button.buttonAndHandler(u"Submit")
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return
        captcha = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='recaptcha'
        )

        if captcha.verify():
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
    fields['captcha'].widgetFactory = ReCaptchaFieldWidget

    @button.buttonAndHandler(u"Submit")
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage

            return
        captcha = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='recaptcha'
        )

        if captcha.verify():
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

            return mail_host.send(mime_msg.as_string())
        else:
            self.description = u"Please complete the Captcha."


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

        reports = reversed( sorted(report.items(), key=lambda x: int(x[1]) ))

        return islice(reports, 0, 10)
