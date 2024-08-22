from eea.climateadapt.interfaces import ICCACountry
from zope.component import adapter, getMultiAdapter
from plone.restapi.interfaces import IExpandableElement
from zope.interface import implementer
from zope.interface import Interface
import lxml.html
from lxml import etree


@implementer(IExpandableElement)
@adapter(ICCACountry, Interface)
class CountryProfile(object):
    """An expander that automatically inserts the HTML rendering of a country profile view
    (the @@country-profile) into the components of country profile serialization
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        data = {
            "menu": [],
            "content": [],
            "html": None,
            "updated": None,
            "message_top": None,
            "top_accordeon": None,
        }
        if self.context.getId().lower() in ["turkiye", "turkey"]:
            for annot in list(self.context.__annotations__):
                if (
                    "plone.tiles.data." in annot
                    and "text" in self.context.__annotations__[annot]
                    and None == self.context.__annotations__[annot]["title"]
                ):
                    html = self.context.__annotations__[annot]["text"].output
        elif self.context.getId().lower() in ["norway", "liechtenstein"]:
            for annot in list(self.context.__annotations__):
                if (
                    "plone.tiles.data." in annot
                    and "text" in self.context.__annotations__[annot]
                    and "main content" == self.context.__annotations__[annot]["title"]
                ):
                    html = self.context.__annotations__[annot]["text"].output
        else:
            view = getMultiAdapter(
                (self.context, self.request), name="country-profile")
            html = view().replace("<tal>", "").replace("</tal>", "")

        e = lxml.html.fromstring(html)

        if self.context.getId().lower() in [
            "turkiye",
            "turkey",
            "norway",
            "liechtenstein",
        ]:
            menus = e.xpath(
                '//div[contains(@class,"sweet-tabs")]//ul[contains(@class,"nav-tabs")]//a'
            )
            for menu in menus:
                data["menu"].append(
                    {"id": menu.attrib["href"][1:], "name": menu.text})
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
                            [etree.tostring(child)
                             for child in aer[0].iterchildren()]
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
                data["menu"].append(
                    {"id": menu.attrib["href"][1:], "name": menu.text})
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
                        menuContent.append(
                            {"type": "accordeon", "value": accordeon})
                        accordeon = []
                    menuContent.append({"type": "h2", "value": content.text})
                elif content.tag == "table":
                    if len(accordeon):
                        menuContent.append(
                            {"type": "accordeon", "value": accordeon})
                        accordeon = []
                    menuContent.append(
                        {"type": "table", "value": etree.tostring(content)}
                    )
                elif (
                    content.tag == "div"
                    and "class" in content.attrib
                    and content.attrib["class"] == "panel panel-default"
                ):
                    aer = content.xpath(
                        './/div[contains(@class,"panel-body")]')
                    accordeon.append(
                        {
                            "title": content.xpath(
                                './div[contains(@class,"panel-heading")]//a/span'
                            )[0].text,
                            "value": "".join(
                                [
                                    etree.tostring(child)
                                    for child in aer[0].iterchildren()
                                ]
                            ),
                        }
                    )
                elif content.tag == "div":
                    if len(accordeon):
                        menuContent.append(
                            {"type": "accordeon", "value": accordeon})
                        accordeon = []
                    aer = content.xpath("./*")
                    menuContent.append(
                        {"type": "div", "value": "".join(
                            map(etree.tostring, aer))}
                    )
                # for norway and lichenstein
                elif content.tag == "h3":
                    if len(accordeon):
                        menuContent.append(
                            {"type": "accordeon", "value": accordeon})
                        accordeon = []
                    menuContent.append({"type": "h3", "value": content.text})
                elif content.tag == "p":
                    if len(accordeon):
                        menuContent.append(
                            {"type": "accordeon", "value": accordeon})
                        accordeon = []
                    aer = content.xpath("./*")
                    # menuContent.append({'type':'p', 'value':''.join(map(etree.tostring,aer))})
                    menuContent.append(
                        {
                            "type": "p",
                            "value": "".join(
                                [
                                    etree.tostring(child)
                                    for child in content.iterchildren()
                                ]
                            ),
                        }
                    )
            if len(accordeon):
                menuContent.append({"type": "accordeon", "value": accordeon})
            data["content"].append(menuContent)

        result = {
            "countryprofile": {
                "@id": "{}/@countryprofile".format(self.context.absolute_url()),
                "html": data,
            }
        }

        return result
