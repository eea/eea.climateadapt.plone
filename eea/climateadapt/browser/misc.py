import json
import logging
import urllib.error
import urllib.parse

# import re
import urllib.request

# from datetime import datetime
# from email.mime.text import MIMEText
# from io import BytesIO
from itertools import islice

import requests
import transaction
from OFS.ObjectManager import BeforeDeleteException
from plone import api
from plone.api import portal
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy

# from plone.app.widgets.dx import DatetimeWidgetConverter as BaseConverter
from plone.memoize import view
from Products.CMFPlone.utils import getToolByName, isExpired
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.interface import Interface, implementer

# from dateutil.tz import gettz
# from eea.climateadapt.config import CONTACT_MAIL_LIST
# from eea.climateadapt.schema import Email

from eea.climateadapt.translation.utils import (
    filters_to_query,
    get_current_language,
)


# from eea.climateadapt.translation.utils import (
#     filters_to_query,
#     get_current_language,
# )

# from plone.api.portal import show_message
# from plone.formwidget.captcha.validator import CaptchaValidator, WrongCaptchaCode
# from plone.formwidget.captcha.widget import CaptchaFieldWidget
# from plone.z3cform.layout import wrap_form
# from Products.statusmessages.interfaces import IStatusMessage
# from z3c.form import button, field, validator
# from zope import schema
# from eea.climateadapt.config import CONTACT_MAIL_LIST
# from eea.climateadapt.schema import Email

logger = logging.getLogger("eea.climateadapt")


class Captcha(object):
    subject = ""
    captcha = ""

    def __init__(self, context):
        self.context = context


class NewsletterRedirect(BrowserView):
    """Redirect to newsletter #84251"""

    def __call__(self):
        return self.request.response.redirect("/newsletter")


class WebEmptyView(BrowserView):
    """Empty view for /web #84251"""

    def __call__(self):
        return self.request.response.redirect("/newsletter")


class CalculateItemStatistics(BrowserView):
    """Performs a catalog search for the portal types defined in the search()
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
        """Initializing Annotations"""
        logger.info("Initializing Annotations")
        annot = IAnnotations(self.context)
        annot["cca-item-statistics"] = {}
        types = getToolByName(self.context, "portal_types").listContentTypes()

        for year in range(1969, 2018):
            annotation = {}

            for ctype in types:
                annotation[ctype] = {"published": 0, "total": 0}
            annot["cca-item-statistics"][year] = annotation
        logger.info("Finished Initializing Annotations")

    def search(self):
        """Catalog search for all content types used"""
        logger.info("Starting the catalog search")
        catalog = self.context.portal_catalog
        query = {
            "portal_type": [
                "eea.climateadapt.aceproject",
                "eea.climateadapt.tool",
                "eea.climateadapt.researchproject",
                "eea.climateadapt.publicationreport",
                "eea.climateadapt.organisation",
                "eea.climateadapt.mapgraphdataset",
                "eea.climateadapt.informationportal",
                "eea.climateadapt.indicator",
                "eea.climateadapt.guidancedocument",
                "eea.climateadapt.casestudy",
                "eea.climateadapt.adaptationoption",
                "Link",
                "Document",
                "News Item",
                "Event",
                "collective.cover.content",
                "Folder",
                "EasyForm",
                "Collection",
            ]
        }

        brains = catalog.searchResults(**query)
        logger.info("Got %s results." % len(brains))
        items_count = 0

        for brain in brains:
            if items_count % 100 == 0:
                logger.info("Went through %s brains" % items_count)
            obj = brain.getObject()
            obj_state = api.content.get_state(obj)
            creation_year = obj.created().year()
            portal_type = obj.portal_type

            url = obj.absolute_url()

            if creation_year is None:
                logger.info("No creation date found for %s" % url)

                continue

            self.saveToAnnotations(creation_year, portal_type, False)

            if obj_state == "published":
                publish_year = obj.effective().year()

                if publish_year is None:
                    logger.info("No publishing date found for %s" % url)

                    continue
                self.saveToAnnotations(publish_year, portal_type, True)
            items_count += 1
        logger.info("Finished the search.")

    def saveToAnnotations(self, year, content_type, published):
        """Saves the number of brains depending on its review state"""
        annotations = IAnnotations(self.context)["cca-item-statistics"]

        if published:
            annotations[year][content_type]["published"] += 1
        annotations[year][content_type]["total"] += 1

    def cleanUpData(self):
        """Cleans up all the unnecessary indexes"""
        logger.info("Cleaning up DATA")

        for year in range(1969, 2018):
            annot = IAnnotations(self.context)
            annotation = annot["cca-item-statistics"][year]
            keys = annotation.keys()

            for key in keys:
                if annotation[key]["total"] == 0:
                    annotation.pop(key, None)
            keys = list(annotation.keys())

            if len(keys) == 0:
                IAnnotations(self.context)["cca-item-statistics"].pop(year)

                continue
        logger.info("Finished cleaning up data")


class getItemStatistics(BrowserView):
    """BrowserView used in order to display the total number of brains present
    on the site in each year

    path: site/@@get-item-statistics
    """

    def __call__(self):
        return self.index()

    def get_portal_types(self, year):
        """Filters out the portal types"""
        all_types = [
            {xx[0]: xx[1].title} for xx in self.context.portal_types.objectItems()
        ]
        annotations = IAnnotations(self.context)["cca-item-statistics"]

        types = []

        for pair in all_types:
            if list(pair.keys())[0] in list(annotations[year].keys()):
                types.append(pair)

        return types

    def get_years(self):
        """Gets the years present in IAnnotations and sorts them ascending"""
        years = IAnnotations(self.context)["cca-item-statistics"].keys()
        years.sort()

        return years

    def get_published(self, year, portal_type):
        """Gets the number of published items depending on year/portal_type"""
        annotations = IAnnotations(self.context)["cca-item-statistics"]

        return annotations[year][portal_type]["published"]

    def get_total(self, year, portal_type):
        """Gets the number of total items depending on year/portal_type"""
        annotations = IAnnotations(self.context)["cca-item-statistics"]

        return annotations[year][portal_type]["total"]


class FixCheckout(BrowserView):
    """A view to fix getBaseline error when the original item was deleted
    and only the copy remains.
    """

    def __call__(self):
        policy = ICheckinCheckoutPolicy(self.context, None)
        relation = policy._get_relation_to_baseline()
        relation.from_object = relation.to_object
        relation._p_changed = True

        return "Fixed"


class ISimplifiedResourceRegistriesView(Interface):
    """A view with simplified resource registries"""


@implementer(ISimplifiedResourceRegistriesView)
class TransRegionView(BrowserView):
    """Custom view for /transnational-regions"""


@implementer(ISimplifiedResourceRegistriesView)
class CountriesView(BrowserView):
    """Custom view for http://climate-adapt.eea.europa.eu/countries"""


@implementer(ISimplifiedResourceRegistriesView)
class MapViewerView(BrowserView):
    """Custom view for http://climate-adapt.eea.europa.eu/tools/map-viewer"""

    def __call__(self):
        return self.request.response.redirect(
            "/tools/map-viewer?" + self.request["QUERY_STRING"]
        )


class AdaptationStrategyView(BrowserView):
    """Redirect for http://climate-adapt.eea.europa.eu/adaptation-strategies
    to /countries-view-map
    """

    @view.memoize
    def __call__(self):
        return self.request.response.redirect("/countries")


class RedirectToSearchView(BrowserView):
    """Custom view for /content"""

    def __init__(self, context, request):
        # Each view instance receives context and request as construction parameters
        self.context = context
        self.request = request

    def __call__(self):
        current_language = get_current_language(self.context, self.request)
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )

        typeOfDataTo = self.request.other["ACTUAL_URL"].split("/")[-1]
        typeOfDataValues = {
            "adaptation-options": "Adaptation options",
            "case-studies": "Case studies",
            "indicators": "Indicators",
            "portals": "Information portals",
            "guidances": "Guidance",
            "organisations": "Organisations",
            "publications": "Publications and reports",
            "projects": "Research and knowledge projects",
            "tools": "Tools",
            "videos": "Videos",
        }

        navigation_root_url = portal_state.navigation_root_url()
        if "/observatory" in navigation_root_url:
            link = "/" + current_language + "/observatory/catalogue/"
        else:
            link = "/" + current_language + "/data-and-downloads/"

        if (
            link == "/" + current_language + "/observatory/catalogue/"
            and typeOfDataTo == "organisations"
        ):
            link = (
                "/"
                + current_language
                + "/observatory/About/about-the-observatory#partners"
            )
        else:
            querystring = self.request.form.get("SearchableText", "")
            query = {
                "display_type": "list",
                "highlight": {"fields": {"*": {}}},
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"hasWorkflowState": "published"}},
                            {
                                "query_string": {
                                    "analyze_wildcard": True,
                                    "default_operator": "OR",
                                    "query": querystring,
                                }
                            },
                        ]
                    }
                },
            }
            if typeOfDataTo in typeOfDataValues:
                query["query"]["bool"]["filter"] = {
                    "bool": {
                        "should": [
                            {"term": {"typeOfData": typeOfDataValues[typeOfDataTo]}}
                        ]
                    }
                }

            link = (
                link
                + "?source="
                + urllib.parse.quote(json.dumps(query))
                + "&lang="
                + current_language
            )

        return self.request.response.redirect(link)


class ExcelCsvExportView(BrowserView):
    """View with links to the excel export for portal types"""


class ClearMacrotransnationalRegions(BrowserView):
    """Clear the macrotransnational regions from geographic localization

    if all the regions are selected
    """

    def __call__(self):
        return
        logger.info("Starting to clear regions.")

        for brain in self.catalog_search():
            self.clear_regions(brain.getObject())
        logger.info("Finished clearing regions.")

    def catalog_search(self):
        catalog = self.context.portal_catalog
        query = {
            "portal_type": [
                "eea.climateadapt.aceproject",
                "eea.climateadapt.adaptationoption",
                "eea.climateadapt.casestudy",
                "eea.climateadapt.guidancedocument",
                "eea.climateadapt.indicator",
                "eea.climateadapt.informationportal",
                "eea.climateadapt.mapgraphdataset",
                "eea.climateadapt.organisation",
                "eea.climateadapt.publicationreport",
                "eea.climateadapt.researchproject",
                "eea.climateadapt.tool",
            ]
        }
        brains = catalog.searchResults(**query)

        return brains

    def clear_regions(self, obj):
        if obj.geochars in [None, "", "", []]:
            return

        geochars = json.loads(obj.geochars)
        macro = geochars["geoElements"].get("macrotrans", [])

        if macro:
            if len(macro) == 13:
                logger.info("Clearing regions on %s" % obj.absolute_url())
                geochars["geoElements"]["macrotrans"] = []
                geochars = json.dumps(geochars).encode()
                obj.geochars = geochars
                obj._p_changed = True
                obj.reindexObject()


class GetItemsForMacrotransRegions(BrowserView):
    """Write to files the url of objects belonging to either the caribbean
    or se-europe region

    NOTE: this is one time use only view
    """

    def __call__(self):
        return

        for b in self.catalog_search():
            obj = b.getObject()

            if obj.geochars in [None, "", "", []]:
                continue
            geochars = json.loads(obj.geochars)
            macro = geochars["geoElements"].get("macrotrans", [])

            if macro:
                if "TRANS_MACRO_CAR_AREA" in macro:
                    self.write_caribbean(obj)

                if "TRANS_MACRO_SE_EUR" in macro:
                    self.write_se_europe(obj)
        logger.info("Completed writing to files.")

    def write_caribbean(self, obj):
        logger.info("Writing %s to CARIBBEAN" % obj.absolute_url())
        with open("/".join(["/tmp/", "caribbean"]), "a") as f:
            f.writelines("Object URL: %s \n" % obj.absolute_url())

    def write_se_europe(self, obj):
        logger.info("Writing %s to SE EUROPE" % obj.absolute_url())
        with open("/".join(["/tmp/", "se-europe"]), "a") as f:
            f.writelines("Object URL: %s \n" % obj.absolute_url())

    def catalog_search(self):
        catalog = self.context.portal_catalog
        query = {
            "portal_type": [
                "eea.climateadapt.aceproject",
                "eea.climateadapt.adaptationoption",
                "eea.climateadapt.casestudy",
                "eea.climateadapt.guidancedocument",
                "eea.climateadapt.indicator",
                "eea.climateadapt.informationportal",
                "eea.climateadapt.mapgraphdataset",
                "eea.climateadapt.organisation",
                "eea.climateadapt.publicationreport",
                "eea.climateadapt.researchproject",
                "eea.climateadapt.tool",
            ]
        }
        brains = catalog.searchResults(**query)

        return brains


def _archive_news(site):
    """Script that will get called by cron once per day"""
    catalog = getToolByName(site, "portal_catalog")
    query = {"portal_type": ["News Item", "Link", "Event"], "review_state": "published"}
    brains = catalog.searchResults(**query)

    for b in brains:
        obj = b.getObject()
        # if isExpired(obj) == 1 and api.content.get_state(obj) != 'archived':

        if isExpired(obj) == 1:
            logger.info("Archiving %s" % obj.absolute_url())
            api.content.transition(obj, "archive")
            transaction.commit()


# class IContactForm(form.Schema):
#     name = schema.TextLine(title="Name:", required=True)
#     email = Email(title="Email:", required=True)
#     feedback = schema.Choice(
#         title="Type of feedback:",
#         required=True,
#         values=[
#             "Request for information",
#             "Suggestion for Improvement",
#             "Broken link",
#         ],
#     )
#     message = schema.Text(title="Message:", required=True)
#
#     captcha = schema.TextLine(title="Captcha", description="", required=False)


# class ContactForm(form.SchemaForm):
#     """Contact Form"""
#
#     schema = IContactForm
#     ignoreContext = True
#
#     label = "Contact CLIMATE-ADAPT"
#     description = """ Please use the contact form below if you have questions
#     on CLIMATE-ADAPT, to suggest improvements for CLIMATE-ADAPT or to report
#     broken links.
#     """
#
#     fields = field.Fields(IContactForm)
#     fields["captcha"].widgetFactory = CaptchaFieldWidget
#
#     @button.buttonAndHandler("Submit")
#     def handleApply(self, action):
#         data, errors = self.extractData()
#
#         if errors:
#             self.status = self.formErrorsMessage
#
#             return
#
#         if "captcha" in data:
#             # Verify the user input against the captcha
#             captcha = CaptchaValidator(
#                 self.context, self.request, None, IContactForm["captcha"], None
#             )
#
#             try:
#                 valid = captcha.validate(data["captcha"])
#             except WrongCaptchaCode:
#                 show_message(
#                     message="Invalid Captcha.", request=self.request, type="error"
#                 )
#                 return
#
#             if valid:
#                 mail_host = api.portal.get_tool(name="MailHost")
#                 # emailto = str(api.portal.getSite().email_from_address)
#
#                 mime_msg = MIMEText(data.get("message"))
#                 mime_msg["Subject"] = data.get("feedback")
#                 mime_msg["From"] = data.get("email")
#                 # mime_msg['To'] = ','.join(b for b in CONTACT_MAIL_LIST)
#                 # mime_msg['To'] = CONTACT_MAIL_LIST
#
#                 for m in CONTACT_MAIL_LIST:
#                     mime_msg["To"] = m
#
#                 self.description = "Email Sent."
#                 IStatusMessage(self.request).addStatusMessage(
#                     "Email SENT", "info")
#                 return mail_host.send(mime_msg.as_string())
#             else:
#                 self.description = "Please complete the Captcha."


# class IContactFooterForm(form.Schema):
#     name = schema.TextLine(title="Name:", required=True)
#     email = Email(title="Your Email:", required=True)
#     subject = schema.TextLine(title="Subject", required=True)
#     message = schema.Text(title="Message:", required=True)
#
#     captcha = schema.TextLine(title="Captcha", description="", required=False)


# class ContactFooterForm(form.SchemaForm):
#     """Footer Contact Form"""
#
#     schema = IContactFooterForm
#     ignoreContext = True
#
#     label = "Contact form"
#     description = """ Climate-ADAPT aims to support Europe in adapting to
#     climate change. It is an initiative of the European Commission and helps
#     users to access and share data and information on expected climate change
#     in Europe. Fill in this form to contact the site owners.
#     """
#
#     fields = field.Fields(IContactFooterForm)
#     fields["captcha"].widgetFactory = CaptchaFieldWidget
#
#     @button.buttonAndHandler("Submit")
#     def handleApply(self, action):
#         data, errors = self.extractData()
#
#         if errors:
#             self.status = self.formErrorsMessage
#
#             return
#
#         if "captcha" in data:
#             # Verify the user input against the captcha
#             captcha = CaptchaValidator(
#                 self.context, self.request, None, IContactFooterForm["captcha"], None
#             )
#
#             try:
#                 valid = captcha.validate(data["captcha"])
#             except WrongCaptchaCode:
#                 show_message(
#                     message="Invalid Captcha.", request=self.request, type="error"
#                 )
#                 return
#
#             if valid:
#                 mail_host = api.portal.get_tool(name="MailHost")
#
#                 info = {
#                     "name": data.get("name"),
#                     "mail": data.get("email"),
#                     "url": self.context.absolute_url(),
#                 }
#                 text = (
#                     """
#
# Climate Adapt Website
#
# You are receiving this mail because %(name)s
# %(mail)s
# is sending feedback about the site you administer at %(url)s.
# """
#                     % info
#                 )
#
#             mime_msg = MIMEText(data.get("message") + text)
#             mime_msg["Subject"] = data.get("subject")
#             mime_msg["From"] = data.get("email")
#             mime_msg["To"] = str(api.portal.getSite().email_from_address)
#
#             self.description = "Email Sent."
#
#             IStatusMessage(self.request).addStatusMessage("Email SENT", "info")
#
#             return mail_host.send(mime_msg.as_string())
#         else:
#             self.description = "Please complete the Captcha."


# CaptchaForm = wrap_form(ContactForm)
#
# # Register Captcha validator for the captcha field in the IContactForm
# validator.WidgetValidatorDiscriminators(
#     CaptchaValidator, field=IContactForm["captcha"])
#
#
# CaptchaFooterForm = wrap_form(ContactFooterForm)
#
# # Register Captcha validator for the captcha field in the IContactForm
# validator.WidgetValidatorDiscriminators(
#     CaptchaValidator, field=IContactFooterForm["captcha"]
# )


def preventFolderDeletionEvent(object, event):
    for obj in object.listFolderContents():
        iterate_control = obj.restrictedTraverse("@@iterate_control")

        try:
            if iterate_control.is_checkout():
                # Cancel deletion
                raise BeforeDeleteException
        except AttributeError:
            logger.info("Needs plone6 migration")
            continue


class ViewGoogleAnalyticsReport(BrowserView):
    """A view to view the google analytics report data"""

    def report_data(self):
        site = portal.get()
        report = site.__annotations__.get("google-analytics-cache-data", {})

        reports = reversed(sorted(list(report.items()), key=lambda x: int(x[1])))

        return islice(reports, 0, 10)


# class DatetimeDataConverter(BaseConverter):
#     """Avoid problem with missing tzinfo from default datetime widgets"""

#     def toFieldValue(self, value):
#         logger.warn("dateconvertwidget", value)
#         value = super(DatetimeDataConverter, self).toFieldValue(value)
#         if value is not self.field.missing_value:
#             if not getattr(value, "tzinfo", None):
#                 value = value.replace(tzinfo=gettz())
#         return value


class VibrioProxy(BrowserView):
    url_vibrio = "https://geoportal.ecdc.europa.eu/vibriomapviewer/api/proxy"

    def __call__(self):
        response = self.request.response
        response.setHeader("Content-type", "application/xml")

        url = self.url_vibrio + "?" + self.request["QUERY_STRING"]
        resp = requests.get(url)
        return resp.content


# class GetCoventantOfMayorsLinks(BrowserView):
#     domains = ["www.covenantofmayors.eu", "eumayors.eu", "mayors-adapt.eu"]
#
#     def url_needed(self, url):
#         for domain in self.domains:
#             if domain in url:
#                 return True
#
#         return False
#
#     def data_to_xls(self, data):
#         headers = ["Location", "Link"]
#
#         # Create a workbook and add a worksheet.
#         out = BytesIO()
#         workbook = xlsxwriter.Workbook(out, {"in_memory": True})
#
#         wtitle = "Broken-Links"
#         worksheet = workbook.add_worksheet(wtitle[:30])
#
#         for i, title in enumerate(headers):
#             worksheet.write(0, i, title or "")
#
#         row_index = 1
#
#         for row in data:
#             path = row[0]
#             link = row[1]
#             worksheet.write(row_index, 0, path or "")
#             worksheet.write(row_index, 1, link or "")
#
#             row_index += 1
#
#         workbook.close()
#         out.seek(0)
#
#         return out
#
#     def __call__(self):
#         links = get_links(self.context)
#         result = []
#
#         for link in links:
#             url = link["link"]
#
#             if url and self.url_needed(url):
#                 path = "/".join(link["object_url"])
#                 obj = self.context.unrestrictedTraverse(path)
#                 result.append((obj.absolute_url(), url))
#
#         xlsio = self.data_to_xls(result)
#         sh = self.request.response.setHeader
#
#         sh(
#             "Content-Type",
#             "application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet",
#         )
#         fname = "-".join(
#             ["CovenantOfMayorsLinks", str(
#                 datetime.now().replace(microsecond=0))]
#         )
#         sh("Content-Disposition", "attachment; filename=%s.xlsx" % fname)
#
#         return xlsio.read()


# TODO plone6 this is not used anymore
def create_contributions_link(language="en", organisation_id=None):
    # origin_website vocabulary?
    # https://github.com/eea/eea.climateadapt.plone/blob/master/eea/climateadapt/vocabulary.py#L441

    # filters[0][values][0]=AdapteCCA
    # &filters[0][values][1]=Lancet Countdown
    # &filters[0][values][2]=DRMKC
    # &filters[0][values][3]=EEA-archived
    # &filters[0][values][4]=EEA
    # &filters[0][values][5]=C3S

    map_contributor_values = {
        # not in vocabulary?
        "copernicus-climate-change-service-ecmw": "Copernicus Climate Change Service and Copernicus Atmosphere Monitoring Service",
        "european-centre-for-disease-prevention-and-control-ecdc": "European Centre for Disease Prevention and Control",
        "european-commission": "European Commission",
        "european-food-safety-authority": "European Food Safety Authority",
        "who-regional-office-for-europe-who-europe": "WHO Regional Office for Europe",
        "world-health-organization": "World Health Organization",
        # solved:
        "european-environment-agency-eea": "EEA",
        "lancet-countdown": "Lancet Countdown",
    }

    terms = []

    if organisation_id in map_contributor_values:
        org = map_contributor_values[organisation_id]
        terms.append(("cca_origin_websites.keyword", [org]))
        terms.append(("language", [language]))

        url = "/" + language + "/observatory/catalogue/?"
        # TODO fix query
        # query = filters_to_query(terms)
        query = ""

        return "{}{}".format(url, query)
