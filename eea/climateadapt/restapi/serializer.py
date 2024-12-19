from copy import deepcopy

from lxml.html import fragments_fromstring, tostring
from plone import api
from plone.api import portal
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityContainer, IDexterityContent
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.serializer.blocks import SlateBlockSerializerBase, uid_to_url
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeFolderToJson, SerializeToJson
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from zope.component import adapter, getMultiAdapter
from zope.interface import Interface, implementer

from eea.climateadapt.behaviors import (
    IAceProject,
    IAdaptationOption,
    ICaseStudy,
    IOrganisation,
)
from eea.climateadapt.behaviors.mission_funding_cca import IMissionFundingCCA
from eea.climateadapt.behaviors.mission_tool import IMissionTool
from eea.climateadapt.browser.adaptationoption import find_related_casestudies
from eea.climateadapt.interfaces import IClimateAdaptContent, IEEAClimateAdaptInstalled

from .utils import cca_content_serializer


def serialize(possible_node):
    if isinstance(possible_node, basestring):
        # This happens for some fields that store non-markup values as richtext
        return possible_node
    return tostring(possible_node)


@adapter(IRichText, IDexterityContent, IEEAClimateAdaptInstalled)
class RichttextFieldSerializer(DefaultFieldSerializer):
    def externalize(self, text):
        site = portal.get()
        site_url = site.absolute_url()
        frags = fragments_fromstring(text)
        for frag in frags:
            # el.set("style", None)
            if isinstance(frag, basestring):
                continue
            # remove all style attributes
            for el in frag.xpath("//*[@style]"):
                el.attrib.pop("style", None)
            for link in frag.xpath("a"):
                href = link.get("href")
                if href and not href.startswith(site_url):
                    link.set("target", "_blank")
        res = unicode("\n").join([serialize(e) for e in frags])
        return res

    def __call__(self):
        value = self.get_value()
        output = json_compatible(value, self.context)
        if output:
            portal_transforms = api.portal.get_tool(name="portal_transforms")
            raw_html = output["data"]
            # print("raw", raw_html)
            data = portal_transforms.convertTo(
                "text/x-html-safe", raw_html, mimetype="text/html"
            )
            html = data.getData()
            # print("transformed", html)
            output["data"] = self.externalize(html)

        return output


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IEEAClimateAdaptInstalled)
class SlateBlockSerializer(SlateBlockSerializerBase):
    """SlateBlockSerializerBase."""

    # TODO: this needs also a deserializer that takes the scale in url and saves it to
    # the "scale" field

    def handle_img(self, child):
        if child.get("url"):
            url = uid_to_url(child["url"])
            if child.get("scale"):
                url = "%s/@@images/image/%s" % (url, child["scale"])
            else:
                url = "%s/@@images/image/huge" % url

            child["url"] = url


@adapter(IDexterityContainer, IEEAClimateAdaptInstalled)
class GenericFolderSerializer(SerializeFolderToJson):
    def __call__(self, version=None, include_items=True):
        result = super(GenericFolderSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["language"] = getattr(item, "language", "")

        return result


@adapter(IDexterityContent, IEEAClimateAdaptInstalled)
class GenericContentSerializer(SerializeToJson):
    """Generic content serializer (everything that's not CCA-specific)"""

    def __call__(self, version=None, include_items=True):
        result = super(GenericContentSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["language"] = getattr(item, "language", "")

        return result


@adapter(IClimateAdaptContent, Interface)
class ClimateAdaptContentSerializer(SerializeToJson):
    """Simple CCA content serializer (database items such as Video)"""

    def __call__(self, version=None, include_items=True):
        result = super(ClimateAdaptContentSerializer, self).__call__(
            version=None, include_items=True
        )

        return cca_content_serializer(self.context, result, self.request)


@adapter(IAdaptationOption, Interface)
# SerializeToJson
class AdaptationOptionSerializer(SerializeFolderToJson):
    def __call__(self, version=None, include_items=True):
        result = super(AdaptationOptionSerializer, self).__call__(
            version=None, include_items=True
        )
        result["related_case_studies"] = find_related_casestudies(self.context)
        return cca_content_serializer(self.context, result, self.request)


@adapter(IAceProject, Interface)
class AceProjectSerializer(SerializeFolderToJson):  # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(AceProjectSerializer, self).__call__(
            version=None, include_items=True
        )
        return cca_content_serializer(self.context, result, self.request)


@adapter(ICaseStudy, Interface)
class CaseStudySerializer(SerializeFolderToJson):  # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(CaseStudySerializer, self).__call__(
            version=None, include_items=True
        )
        result = cca_content_serializer(self.context, result, self.request)

        item = self.context
        images = item.contentValues({"portal_type": "Image"})
        suffix = "/@@images/image/large"
        result["cca_gallery"] = [
            {
                "title": image.Title(),
                "url": image.absolute_url() + suffix,
                "description": image.Description(),
                "rights": getattr(image.aq_inner.aq_self, "rights"),
            }
            for image in images
        ]

        return result


@adapter(IMissionFundingCCA, Interface)
class MissionFundingSerializer(SerializeFolderToJson):  # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(MissionFundingSerializer, self).__call__(
            version=None, include_items=True
        )

        obj = self.context

        blocks_copy = deepcopy(obj.blocks)
        blocks_layout = obj.blocks_layout["items"]

        columnblock = None
        for uid in blocks_layout:
            block = blocks_copy[uid]
            if block["@type"] == "columnsBlock":
                columnblock = block

        firstcol_id = columnblock["data"]["blocks_layout"]["items"][0]
        firstcol = columnblock["data"]["blocks"][firstcol_id]

        description = ""
        for i, block_id in enumerate(firstcol["blocks_layout"]["items"]):
            nextuid = None
            if i < len(firstcol["blocks_layout"]["items"]) - 1:
                nextuid = firstcol["blocks_layout"]["items"][i + 1]
            blocks = firstcol["blocks"]
            block = blocks[block_id]
            text = block.get("plaintext", "")

            if "Objective of the funding programme" in text:
                description = blocks[nextuid].get("plaintext")

        if not result.get("description"):
            result["description"] = description

        return result


@adapter(IMissionTool, Interface)
class MissionToolSerializer(SerializeFolderToJson):  # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(MissionToolSerializer, self).__call__(
            version=None, include_items=True
        )

        obj = self.context

        blocks_copy = deepcopy(obj.blocks)
        blocks_layout = obj.blocks_layout["items"]

        columnblock = None
        for uid in blocks_layout:
            block = blocks_copy[uid]
            if block["@type"] == "columnsBlock":
                columnblock = block

        firstcol_id = columnblock["data"]["blocks_layout"]["items"][0]
        firstcol = columnblock["data"]["blocks"][firstcol_id]

        description = ""
        for i, block_id in enumerate(firstcol["blocks_layout"]["items"]):
            nextuid = None
            if i < len(firstcol["blocks_layout"]["items"]) - 1:
                nextuid = firstcol["blocks_layout"]["items"][i + 1]
            blocks = firstcol["blocks"]
            block = blocks[block_id]
            text = block.get("plaintext", "")

            if "Objective(s)" in text:
                description = blocks[nextuid].get("plaintext")

        if not result.get("description"):
            result["description"] = description
        return result


@adapter(IOrganisation, Interface)
class OrganisationSerializer(SerializeFolderToJson):  # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(OrganisationSerializer, self).__call__(
            version=None, include_items=True
        )
        result = cca_content_serializer(self.context, result, self.request)
        view = getMultiAdapter((self.context, self.request), name="view")
        contributions = view.get_contributions()
        for contribution in contributions:
            contribution.pop("date", None)
        result["contributions"] = contributions
        return result
