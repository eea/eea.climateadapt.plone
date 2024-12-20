import logging
import re
from collections import defaultdict
from datetime import datetime
from io import BytesIO

import requests
import transaction
import xlsxwriter
from BeautifulSoup import BeautifulSoup
from DateTime import DateTime
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemataForType
from plone.restapi.behaviors import IBlocks
from plone.restapi.services import Service
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations

from eea.climateadapt.behaviors.aceitem import IAceItem
from eea.climateadapt.restapi.slate import iterate_children

# from plone.api.content import get_state

logger = logging.getLogger("eea.climateadapt")


def convert_to_string(item):
    """Convert to string other types"""

    if not item:
        return ""

    if not isinstance(item, basestring):
        new_item = ""
        try:
            iterator = iter(item)
        except TypeError as err:
            value = getattr(item, "raw", None)

            if value:
                return value
            logger.error(err)

            return ""
        else:
            for i in iterator:
                new_item += i

        return new_item

    return item


def discover_links(string_to_search):
    """Use regular expressions to get all urls in string"""
    # REGEX = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.]
    # [a-z]{2,4}/)(?:[^\s()<>]|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>
    # ]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?\xab\xbb\u201c\u201d\u2018
    # \u2019]))')
    REGEX = re.compile(
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )

    try:
        result = re.findall(REGEX, string_to_search) or []

        if isinstance(result, basestring):
            result = [result]
    except Exception as err:
        logger.error(err)
        result = []

    return result


def check_link_status(link):
    """Check the links and return only the broken ones with the respective
    status codes
    """
    if link:
        if isinstance(link, unicode):
            try:
                link = link.encode()
            except UnicodeEncodeError:
                logger.info("UnicodeEncodeError on link %s", link)

                return {"status": 504, "url": link}

        link = link.strip()

        if (
            link.startswith(".")
            or ("resolveuid" in link)
            or ("climate-adapt.eea" in link)
        ):
            return None

        if not link.startswith("http"):
            link = "https://" + link

        link = link.replace("http://", "https://")

        # return {"status": "404", "url": link}

        logger.warning("Now checking: %s", link)

        try:
            resp = requests.head(link, timeout=5, allow_redirects=True)
            if resp.status_code == 404:
                return {"status": "NotFound", "url": link}
            # requests.head(link, timeout=5, allow_redirects=True)
        except requests.exceptions.ReadTimeout:
            return {"status": "ReadTimeout", "url": link}
        except requests.exceptions.ConnectTimeout:
            logger.info("Timed out.")
            logger.info("Trying again with link: %s", link)
            try:
                requests.head(link, timeout=30, allow_redirects=True)
            except Exception:
                return {"status": "NotFound", "url": link}
        except requests.exceptions.TooManyRedirects:
            logger.info("Redirected.")
            logger.info("Trying again with link: %s", link)
            try:
                requests.head(link, timeout=30, allow_redirects=True)
            except Exception:
                return {"status": "Redirected", "url": link}
        except requests.exceptions.URLRequired:
            return {"status": "BrokenUrl", "url": link}
        except requests.exceptions.ProxyError:
            return {"status": "ProxyError", "url": link}
        except requests.exceptions.HTTPError:
            return {"status": "UnknownError", "url": link}
        except Exception:
            return {"status": "NotFound", "url": link}

    return


# PORTAL_TYPES = [
#     "eea.climateadapt.aceproject",
#     "eea.climateadapt.adaptationoption",
#     "eea.climateadapt.casestudy",
#     "eea.climateadapt.guidancedocument",
#     "eea.climateadapt.indicator",
#     "eea.climateadapt.informationportal",
#     "eea.climateadapt.mapgraphdataset",
#     "eea.climateadapt.organisation",
#     "eea.climateadapt.publicationreport",
#     "eea.climateadapt.researchproject",
#     "eea.climateadapt.tool",
#     "collective.cover.content",
#     "Document",
#     "Folder",
# ]


def extract_websites(obj):
    urls = []
    if hasattr(obj, "websites"):
        if isinstance(obj.websites, basestring):
            lines = obj.websites.split(unicode("\n"))
            for line in lines:
                if line.strip():
                    urls.append(line.strip())
        elif type(obj.websites) is list or type(obj.websites) is tuple:
            urls.extend(list(obj.websites))

    return urls


def extract_richtext(obj, fieldname):
    urls = []
    field = getattr(obj, fieldname, "")

    if isinstance(field, RichTextValue):
        text = field.output
        if text:
            bs = BeautifulSoup(text)
            links = bs.findAll("a", attrs={"href": re.compile("^https?://")})
            urls.extend([link.get("href") for link in links])
    elif isinstance(field, basestring):
        urls = discover_links(field)

    return urls


def convert_aceitem(obj):
    urls = extract_websites(obj)
    urls += extract_richtext(obj, "long_description")
    urls += extract_richtext(obj, "description")
    urls += extract_richtext(obj, "source")
    urls += extract_richtext(obj, "comments")
    return urls


def iterate_blocks(obj):
    blocks = getattr(obj, "blocks", None)
    layout = getattr(obj, "blocks_layout", {})

    if not blocks:
        raise StopIteration

    if layout:
        items = layout.get("items")
        for uid in items:
            block = blocks.get(uid)
            if block:
                yield block


def handle_link(node):
    url = node.get("data", {}).get("url")
    return url


SLATE_NODE_HANDLERS = {"link": handle_link}


def extract_slate(block):
    value = (block or {}).get("value", [])
    children = iterate_children(value or [])
    urls = []

    for child in children:
        node_type = child.get("type")
        if node_type:
            handler = SLATE_NODE_HANDLERS.get(node_type)
            if handler:
                link = handler(child)
                if link:
                    urls.append(link)

    return urls


BLOCK_EXTRACTORS = {"slate": extract_slate}


def convert_blocks(obj):
    urls = []
    for block in iterate_blocks(obj):
        if not block:
            continue
        extractor = BLOCK_EXTRACTORS.get(block.get("@type"))
        if extractor:
            urls.extend(extractor(block))
    return urls


CONVERTORS = {
    IAceItem: convert_aceitem,
    IBlocks: convert_blocks,
}

PORTAL_TYPES_BLACKLIST = [
    "ATBooleanCriterion",
    "ATCurrentAuthorCriterion",
    "ATDateCriteria",
    "ATDateRangeCriterion",
    "ATListCriterion",
    "ATPathCriterion",
    "ATRelativePathCriterion",
    "ATPortalTypeCriterion",
    "ATReferenceCriterion",
    "ATSelectionCriterion",
    "ATSimpleIntCriterion",
    "ATSimpleStringCriterion",
    "ATSortCriterion",
    "Discussion Item",
    "Plone Site",
    "TempFolder",
    "Collection",
    # "Document",
    # "Folder",
    "Link",
    "File",
    "Image",
    # "News Item",
    # "Event",
    # "collective.cover.content",
    "EasyForm",
    # "eea.climateadapt.aceproject",
    # "eea.climateadapt.adaptationoption",
    # "eea.climateadapt.casestudy",
    # "eea.climateadapt.guidancedocument",
    # "eea.climateadapt.indicator",
    # "eea.climateadapt.informationportal",
    # "eea.climateadapt.mapgraphdataset",
    # "eea.climateadapt.organisation",
    # "eea.climateadapt.publicationreport",
    # "eea.climateadapt.researchproject",
    # "eea.climateadapt.tool",
    "Topic",
    "PDFTool",
    "PDFTheme",
    "AliasVocabulary",
    "SimpleVocabulary",
    "SimpleVocabularyTerm",
    "SortedSimpleVocabulary",
    "TreeVocabulary",
    "TreeVocabularyTerm",
    "VdexFileVocabulary",
    "VocabularyLibrary",
    "DepictionTool",
    "RichImage",
]


def recursively_extract_links(site):
    """Gets the links for all our items by using the websites field
    along with the respective object urls
    """

    catalog = getToolByName(site, "portal_catalog")
    types = getToolByName(site, "portal_types").listTypeInfo()

    convertors = defaultdict(list)
    for _type in types:
        portal_type = _type.getId()
        if portal_type in PORTAL_TYPES_BLACKLIST:
            continue
        for schemata in iterSchemataForType(portal_type):
            for iface in [schemata] + list(schemata.getBases()):
                convertor = CONVERTORS.get(iface)
                if convertor:
                    convertors[portal_type].append(convertor)

    urls = []

    brains = catalog.searchResults(path="/cca/en")
    count = 0
    logger.info("Got %s objects" % len(brains))

    for b in brains:
        obj = b.getObject()
        path = obj.getPhysicalPath()

        for convertor in convertors[b.portal_type]:
            urls.extend(
                [
                    {"link": link, "object_url": "/".join(path)}
                    for link in convertor(obj)
                ]
            )

        count += 1

        if count % 100 == 0:
            logger.info("Done %s objects" % count)

    logger.info("Finished getting links.")

    return urls


def compute_broken_links(site):
    """Script that will get called by cron once per day"""

    results = []
    links = recursively_extract_links(site)
    annot = IAnnotations(site)["broken_links_data"]

    for info in links:
        if info["link"].startswith("/"):
            continue
            # import pdb
            #
            # pdb.set_trace()
        res = check_link_status(info["link"])
        if res is not None:
            res["object_url"] = info["object_url"]
            results.append(res)

    now = DateTime()
    annot[now] = results
    dates = annot.keys()

    if len(dates) >= 5:  # maximum no. of dates stored
        # delete oldest data except 'pre_nov7_data'
        del annot[sorted(dates)[0]]

    IAnnotations(site)._p_changed = True
    transaction.commit()


class DetectBrokenLinksView(BrowserView):
    def __call__(self):
        compute_broken_links(self.context)
        return "ok"


class BrokenLinksService(Service):
    """Get workflow information"""

    items_to_display = 200

    def results(self):
        portal = api.portal.get()
        annot = IAnnotations(portal)["broken_links_data"]
        latest_dates = sorted(annot.keys())[-5:]
        res = {}

        broken_links = []

        # __import__("pdb").set_trace()
        for date in latest_dates:
            for info in annot[date]:
                if "en" not in info["object_url"]:
                    continue

                item = {}

                # try:
                #     obj = self.context.unrestrictedTraverse(info["object_url"])
                # except:
                #     continue
                # state = get_state(obj)
                state = None
                if state not in ["private", "archived"]:
                    if "climate-adapt.eea" in info["url"]:
                        item["state"] = "internal"
                    else:
                        item["state"] = "external"

                    item["date"] = date.Date() if isinstance(date, DateTime) else date
                    if isinstance(date, str) and date == "pre_nov7_data":
                        continue

                    item["url"] = info["url"]
                    item["status"] = info["status"]
                    item["object_url"] = info["object_url"].replace("/cca/", "/")

                    broken_links.append(item)

        broken_links.sort(key=lambda i: i["date"])

        for link in broken_links:
            res[link["url"]] = link

        return res

    def data_to_xls(self, data):
        headers = [
            ("url", "Destination Links"),
            ("status", "Status Code"),
            ("object_url", "Object Url"),
            ("date", "Date"),
            ("state", "Type"),
        ]

        # Create a workbook and add a worksheet.
        out = BytesIO()
        workbook = xlsxwriter.Workbook(out, {"in_memory": True})

        wtitle = "Broken-Links"
        worksheet = workbook.add_worksheet(wtitle[:30])

        for i, (key, title) in enumerate(headers):
            worksheet.write(0, i, title or "")

        row_index = 1

        for chunk in data:
            for url, row in chunk.items():
                for i, (key, title) in enumerate(headers):
                    value = row[key]
                    worksheet.write(row_index, i, value or "")

                row_index += 1

        workbook.close()
        out.seek(0)

        return out

    def download_as_excel(self):
        xlsdata = self.results()
        xlsio = self.data_to_xls(xlsdata)
        sh = self.request.response.setHeader

        sh(
            "Content-Type",
            "application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet",
        )
        fname = "-".join(["Broken-Links", str(datetime.now().replace(microsecond=0))])
        sh("Content-Disposition", "attachment; filename=%s.xlsx" % fname)

        return xlsio.read()

    def reply(self):
        if "download-excel" in self.request.form:
            return self.download_as_excel()

        info = {
            "@id": self.context.absolute_url() + "/@broken_links",
            "broken_links": self.results(),
        }

        return info
