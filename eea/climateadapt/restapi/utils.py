import json

from bs4 import BeautifulSoup
from plone.dexterity.utils import iterSchemata
from plone.restapi.serializer.converters import json_compatible
from zope.schema import getFields
from plone.restapi.serializer.blocks import uid_to_url

from eea.climateadapt.browser import get_date_updated, get_files
from eea.climateadapt.vocabulary import BIOREGIONS, ace_countries_dict


def get_geographic(item, result={}):
    if not hasattr(item, "geochars") and not item.geochars:
        return result

    response = {}
    if item.geochars is not None and item.geochars != "":
        data = json.loads(item.geochars)
    else:
        data = {}

    if not data:
        return result

    if "countries" in data["geoElements"] and len(data["geoElements"]["countries"]):
        response["countries"] = [
            ace_countries_dict.get(x, x) for x in data["geoElements"]["countries"]
        ]
    if (
        "macrotrans" in data["geoElements"]
        and data["geoElements"]["macrotrans"]
        and len(data["geoElements"]["macrotrans"])
    ):
        response["transnational_region"] = [
            BIOREGIONS.get(x, x) for x in data["geoElements"]["macrotrans"]
        ]

    if len(response):
        result["geographic"] = response

    return result


def use_blocks_from_fti(context, result):
    blocks = None
    blocks_layout = None

    for schema in iterSchemata(context):
        for name, field in getFields(schema).items():
            if name == "blocks" and field.default and not blocks:
                blocks = field.default
            if name == "blocks_layout" and field.default and not blocks_layout:
                blocks_layout = field.default
    if blocks:
        result["blocks"] = blocks
        result["blocks_layout"] = blocks_layout

    return result


def cca_content_serializer(item, result, request):
    """A generic enrichment that should be applied to all IClimateAdaptContent"""

    result = get_geographic(item, result)

    files = get_files(item)
    if files:
        result["cca_files"] = [
            {"title": file.Title(), "url": file.absolute_url()} for file in files
        ]

    dates = get_date_updated(item)

    if (
        hasattr(item, "long_description")
        and item.long_description
        and item.long_description.output
        and "eea_index" in request.form
    ):
        converted = item.portal_transforms.convertTo(
            "text/plain", item.long_description.output
        )
        if converted is not None:
            description = converted.getData().strip()
            try:
                if isinstance(description, str):
                    result["description"] = description
                else:
                    result["description"] = description.decode("utf-8")
            except Exception:
                result["description"] = description.encode("utf-8")
        else:
            result["description"] = ""

    result["cca_last_modified"] = json_compatible(
        dates["cadapt_last_modified"])
    result["cca_published"] = json_compatible(dates["cadapt_published"])
    result["is_cca_content"] = True
    result["language"] = getattr(item, "language", "en")

    result = use_blocks_from_fti(item, result)

    return result


def html_to_plain_text(html, inline_links=True):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    if inline_links:
        for a in soup.find_all("a"):
            href = a.get("href")
            text = a.get_text().strip()
            if href:
                a.replace_with(f"{text} ({href})")
            else:
                a.replace_with(text)
    plain_text = soup.get_text(separator=" ").strip()
    return " ".join(plain_text.split())


def slate_to_html(block):
    def render_child(node):
        if "text" in node:
            return node["text"]

        node_type = node.get("type", "")
        if node_type in ("b", "strong"):
            inner = "".join(render_child(c) for c in node.get("children", []))
            return f"<b>{inner}</b>"

        if node_type == "link":
            href = node.get("data", {}).get("url", "#")
            if href and "resolveuid" in href:
                href = uid_to_url(href)
            inner = "".join(render_child(c) for c in node.get("children", []))
            return f'<a href="{href}" rel="noopener">{inner}</a>'

        if "children" in node:
            return "".join(render_child(c) for c in node["children"])
        return ""

    def render_node(node):
        node_type = node.get("type", "")
        inner = "".join(render_child(c) for c in node.get("children", []))

        if node_type in ("p", "paragraph"):
            return f"<p>{inner}</p>"
        if node_type in ("ul", "ol"):
            items = [render_child(c) for c in node.get("children", [])]
            return " ".join(items)
        if "li" in node_type:
            return f"{inner} "
        return inner

    html = ""
    for node in block.get("value", []):
        html += render_node(node)
    return html


def extract_section_text(blocks, items, start_title, end_title=None):
    start_idx = next(
        (i for i, bid in enumerate(items)
         if start_title in blocks[bid].get("plaintext", "")),
        None,
    )
    end_idx = None
    if end_title:
        end_idx = next(
            (i for i, bid in enumerate(items)
             if end_title in blocks[bid].get("plaintext", "")),
            None,
        )

    if start_idx is None:
        return ""

    content_slice = items[start_idx + 1:end_idx] if end_idx else items[start_idx + 1:]
    parts = []

    for bid in content_slice:
        block = blocks[bid]
        if block.get("@type") != "slate":
            continue

        text = block.get("plaintext", "").strip()
        has_links = any(
            c.get("type") == "link"
            for v in block.get("value", [])
            for c in v.get("children", [])
            if isinstance(c, dict)
        )

        if text and not has_links:
            parts.append(text)
            continue

        html = slate_to_html(block).strip()
        if html and html not in ("<p></p>", "<p><br></p>", "<p>&nbsp;</p>"):
            plain_text = html_to_plain_text(html, inline_links=True)
            if plain_text:
                parts.append(plain_text)

    if not parts:
        return ""

    text = ". ".join(p.strip().rstrip(".") for p in parts if p.strip())
    return text.strip()


def richtext_to_plain_text(value):
    if isinstance(value, dict) and "data" in value:
        html = value.get("data", "")
        return html_to_plain_text(html, inline_links=False)
    return value
