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
from zope.component import adapter
from zope.interface import Interface, implementer
from plone.app.contenttypes.interfaces import ILink

from eea.climateadapt.behaviors import IAdaptationOption, ICaseStudy
from eea.climateadapt.behaviors.mission_funding_cca import IMissionFundingCCA
from eea.climateadapt.behaviors.mission_tool import IMissionTool
from eea.climateadapt.browser.adaptationoption import find_related_casestudies
from eea.climateadapt.interfaces import IClimateAdaptContent
from eea.climateadapt.restapi.navigation import ICCARestapiLayer
from plone.restapi.interfaces import IPloneRestapiLayer

import logging
logger = logging.getLogger("eea.climateadapt")

from .utils import cca_content_serializer, extract_section_text, richtext_to_plain_text

def serialize(possible_node):
    if isinstance(possible_node, str):
        # This happens for some fields that store non-markup values as richtext
        return possible_node
    return tostring(possible_node, encoding=str)


@adapter(IRichText, IDexterityContent, ICCARestapiLayer)
class RichttextFieldSerializer(DefaultFieldSerializer):
    def externalize(self, text):
        site = portal.get()
        site_url = site.absolute_url()
        frags = fragments_fromstring(text)
        for frag in frags:
            # el.set("style", None)
            if isinstance(frag, str):
                continue
            # remove all style attributes
            for el in frag.xpath("//*[@style]"):
                el.attrib.pop("style", None)
            for link in frag.xpath("a"):
                href = link.get("href")
                if href and not href.startswith(site_url):
                    link.set("target", "_blank")
        res = str("\n").join([str(serialize(e)) for e in frags])
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
@adapter(IBlocks, ICCARestapiLayer)
class SlateBlockSerializer(SlateBlockSerializerBase):
    """SlateBlockSerializerBase."""

    # TODO: this needs also a deserializer that takes the scale in url and
    # saves it to the "scale" field

    def handle_img(self, child):
        if child.get("url"):
            url = uid_to_url(child["url"])
            if child.get("scale"):
                url = "%s/@@images/image/%s" % (url, child["scale"])
            else:
                if ("@@images") not in url:
                    url = "%s/@@images/image/huge" % url

            child["url"] = url


@adapter(IDexterityContainer, ICCARestapiLayer)
class GenericFolderSerializer(SerializeFolderToJson):
    def __call__(self, version=None, include_items=True):
        result = super(GenericFolderSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["language"] = getattr(item, "language", "")

        return result


@adapter(IDexterityContent, ICCARestapiLayer)
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


# @adapter(IAceProject, Interface)
# class AceProjectSerializer(SerializeFolderToJson):  # SerializeToJson
#     def __call__(self, version=None, include_items=True):
#         result = super(AceProjectSerializer, self).__call__(
#             version=None, include_items=True
#         )
#         return cca_content_serializer(self.context, result, self.request)


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
        blocks_layout = obj.blocks_layout.get("items", [])

        columnblock = next(
            (b for uid in blocks_layout
             for b in [blocks_copy.get(uid)]
             if b and b.get("@type") == "columnsBlock"),
            None
        )
        if not columnblock:
            return result

        firstcol_id = columnblock["data"]["blocks_layout"]["items"][0]
        firstcol = columnblock["data"]["blocks"][firstcol_id]
        items = firstcol["blocks_layout"]["items"]
        blocks = firstcol["blocks"]

        sections = [
            ("Objective of the funding programme",
             "Type of funding",
             "objective_funding_programme"),
            ("Funding rate (percentage of covered costs)",
             "Expected budget range of proposals",
             "funding_rate"),
            ("Administering authority",
             "Publication page",
             "administering_authority"),
            ("Publication page",
             "General information",
             "publication_page"),
            ("General information",
             "Further information",
             "general_information"),
            ("Further information",
             None,
             "further_information"),
        ]

        for start_title, end_title, field_name in sections:
            result[field_name] = extract_section_text(blocks, items, start_title, end_title) or ""

        if not result.get("description") and result.get("objective_funding_programme"):
            result["description"] = result["objective_funding_programme"]

        if "regions" in result:
            result["funding_region"] = richtext_to_plain_text(result["regions"])

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

        columnblock = {}
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
    
@adapter(ILink, IPloneRestapiLayer)
class LinkRedirectSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        request = self.request
        context = self.context

        if not api.user.is_anonymous():
            return super().__call__(version=version, include_items=include_items)

        target = getattr(context, "remoteUrl", None)

        if not target:
            return super().__call__(version=version, include_items=include_items)

        if "${portal_url}/resolveuid/" in target:
            uid = target.split("/resolveuid/")[-1]
            obj = api.content.get(UID=uid)
            if obj:
                target = obj.absolute_url()
            else:
                logger.warning("Could not resolve UID %s to an object", uid)

        elif "${portal_url}" in target:
            portal_url = api.portal.get().absolute_url()
            target = target.replace("${portal_url}", portal_url)

        # Handle relative paths and resolveuid without ${portal_url}
        if target.startswith('../') or target.startswith('./'):
            from urllib.parse import urljoin
            target = urljoin(context.absolute_url(), target)
        elif '/resolveuid/' in target and not target.startswith('http'):
            uid = target.split('/resolveuid/')[-1].split('/')[0]
            obj = api.content.get(UID=uid)
            if obj:
                target = obj.absolute_url()
            else:
                logger.warning("Could not resolve UID %s to an object", uid)
        raw = getattr(context, "redirection_type", None)

        if raw in (None, ""):
            return super().__call__(version=version, include_items=include_items)

        status = 302
        try:
            candidate = int(str(raw))
            if candidate in (301, 302):
                status = candidate
        except Exception as e:
            logger.warning("Error parsing redirection_type %r: %s", raw, e)

        result = super().__call__(version=version, include_items=include_items)

        if '@components' not in result:
            result['@components'] = {}
        
        result['@components']['redirect'] = {
            'url': target,
            'status': status,
        }
        
        return result

# @adapter(IOrganisation, Interface)
# class OrganisationSerializer(SerializeFolderToJson):  # SerializeToJson
#     def __call__(self, version=None, include_items=True):
#         result = super(OrganisationSerializer, self).__call__(
#             version=None, include_items=True
#         )
#         result = cca_content_serializer(self.context, result, self.request)
#         view = getMultiAdapter((self.context, self.request), name="view")
#         contributions = view.get_contributions()
#         for contribution in contributions:
#             contribution.pop("date", None)
#         result["contributions"] = contributions
#         return result
