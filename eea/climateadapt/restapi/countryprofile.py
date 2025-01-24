import logging

import lxml.html
from lxml import etree
from pkg_resources import resource_filename
from plone.restapi.interfaces import IExpandableElement
from zope.component import adapter, getMultiAdapter
from zope.interface import Interface, implementer

from eea.climateadapt.interfaces import ICCACountry

logger = logging.getLogger("eea.climateadapt")


def load_fixed_countries():
    paths = [
        resource_filename(
            "eea.climateadapt.browser", "data/countryprofiles/turkey.txt"
        ),
        resource_filename(
            "eea.climateadapt.browser", "data/countryprofiles/liechtenstein.txt"
        ),
        resource_filename(
            "eea.climateadapt.browser", "data/countryprofiles/norway.txt"
        ),
    ]

    res = {}
    for path in paths:
        with open(path) as fp:
            data = fp.read()  # .decode("utf-8")
            name = path.split("/")[-1].split(".")[0]
            res[name] = data

    return res


fixed_data = load_fixed_countries()


@implementer(IExpandableElement)
@adapter(ICCACountry, Interface)
class CountryProfile(object):
    """An expander that automatically inserts the HTML rendering of a country profile view
    (the @@country-profile) into the components of country profile serialization
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def make_data(self):
        data = {
            "menu": [],
            "content": [],
            "html": None,
            "updated": None,
            "message_top": None,
            "top_accordeon": None,
        }
        country_id = self.context.getId().lower()
        if country_id in ["turkiye", "turkey"]:
            html = fixed_data["turkey"]
        elif country_id in fixed_data:
            html = fixed_data[country_id]
        else:
            view = getMultiAdapter((self.context, self.request), name="country-profile")
            html = view().replace("<tal>", "").replace("</tal>", "")

        e = lxml.html.fromstring(html)

        if country_id in [
            "turkiye",
            "turkey",
            "norway",
            "liechtenstein",
        ]:
            menus = e.xpath(
                '//div[contains(@class,"sweet-tabs")]//ul[contains(@class,"nav-tabs")]//a'
            )
            for menu in menus:
                data["menu"].append({"id": menu.attrib["href"][1:], "name": menu.text})
            # Check top accordeon, old Turkie page
            contents = e.xpath(
                '//div[contains(@class,"sweet-tabs")]/div/div[contains(@class,"panel panel-default")]'
            )
            accordeon = []
            for content in contents:
                aer = content.xpath('.//div[contains(@class,"panel-body")]')
                accordeon.append(
                    {
                        "title": content.xpath(
                            './div[contains(@class,"panel-heading")]//a/span'
                        )[0].text,
                        "value": "".join(
                            [
                                etree.tostring(child).decode("utf-8")
                                for child in aer[0].iterchildren()
                            ]
                        ),
                    }
                )
            if len(accordeon):
                data["top_accordeon"] = accordeon
            # Check alert top message
            _tmp = e.xpath('//div[contains(@class,"alert-warning")]/p/text()')
            if isinstance(_tmp, list) and len(_tmp):
                data["message_top"] = _tmp[0]
        else:
            menus = e.xpath('//ul[contains(@id,"third-level-menu")]//a')
            for menu in menus:
                data["menu"].append({"id": menu.attrib["href"][1:], "name": menu.text})
            # Check last updated
            _tmp = e.xpath(
                "//strong[contains(text(),'Reporting updated until: ')]/../span/text()"
            )

            if isinstance(_tmp, list) and len(_tmp):
                data["updated"] = _tmp[0]

        for menu in data["menu"]:
            contents = e.xpath('//div[@id="' + menu["id"] + '"]/*')
            menuContent = []
            accordeon = []
            for content in contents:
                if content.tag == "h2":
                    if len(accordeon):
                        menuContent.append({"type": "accordeon", "value": accordeon})
                        accordeon = []
                    menuContent.append({"type": "h2", "value": content.text})
                elif content.tag == "table":
                    if len(accordeon):
                        menuContent.append({"type": "accordeon", "value": accordeon})
                        accordeon = []
                    menuContent.append(
                        {
                            "type": "table",
                            "value": etree.tostring(content).decode("utf-8"),
                        }
                    )
                elif (
                    content.tag == "div"
                    and "class" in content.attrib
                    and content.attrib["class"] == "panel panel-default"
                ):
                    aer = content.xpath('.//div[contains(@class,"panel-body")]')
                    accordeon.append(
                        {
                            "title": content.xpath(
                                './div[contains(@class,"panel-heading")]//a/span'
                            )[0].text,
                            "value": "".join(
                                [
                                    etree.tostring(child).decode("utf-8")
                                    for child in aer[0].iterchildren()
                                ]
                            ),
                        }
                    )
                elif content.tag == "div":
                    if len(accordeon):
                        menuContent.append({"type": "accordeon", "value": accordeon})
                        accordeon = []
                    aer = content.xpath("./*")
                    menuContent.append(
                        {
                            "type": "div",
                            "value": "".join(
                                [etree.tostring(dd).decode("utf-8") for dd in aer]
                            ),
                        }
                    )
                # for norway and lichenstein
                elif content.tag == "h3":
                    if len(accordeon):
                        menuContent.append({"type": "accordeon", "value": accordeon})
                        accordeon = []
                    menuContent.append({"type": "h3", "value": content.text})
                elif content.tag == "p":
                    if len(accordeon):
                        menuContent.append({"type": "accordeon", "value": accordeon})
                        accordeon = []
                    aer = content.xpath("./*")
                    # menuContent.append({'type':'p', 'value':''.join(map(etree.tostring,aer))})
                    menuContent.append(
                        {
                            "type": "p",
                            "value": "".join(
                                [
                                    etree.tostring(child).decode("utf-8")
                                    for child in content.iterchildren()
                                ]
                            ),
                        }
                    )
            if len(accordeon):
                menuContent.append({"type": "accordeon", "value": accordeon})
            data["content"].append(menuContent)

        return data

    def __call__(self, expand=False):
        data = self.make_data()
        try:
            data = self.make_data()
        except Exception as e:
            logger.warning("Error in processing country profile: {}".format(e))

        result = {
            "countryprofile": {
                "@id": "{}/@countryprofile".format(self.context.absolute_url()),
                "html": data,
            }
        }

        return result
