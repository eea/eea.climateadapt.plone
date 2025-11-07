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


def is_h3_block(block):
    if block.get("@type") != "slate":
        return False
    for v in block.get("value", []):
        if v.get("type", "").lower().startswith("h3"):
            return True
    return False


def extract_text_recursive(children):
    parts = []
    for c in children:
        if isinstance(c, str):
            parts.append(c)
        elif isinstance(c, dict):
            if c.get("text"):
                parts.append(c["text"])
            elif "children" in c:
                parts.append(extract_text_recursive(c["children"]))
    return "".join(parts)


def render_slate_value(value):
    parts = []

    def render_children(children):
        segs = []
        for c in children:
            if isinstance(c, dict):
                if c.get("type") == "link":
                    url = c.get("data", {}).get("url", "")
                    if url and "resolveuid" in url:
                        url = uid_to_url(url)
                    label = extract_text_recursive(c.get("children", [])).strip()
                    if label and url:
                        segs.append(f"{label} ({url})")
                    elif url:
                        segs.append(url)
                elif c.get("type") in ("ul", "ol"):
                    segs.append(render_list(c))
                elif c.get("type") == "li":
                    text = extract_text_recursive(c.get("children", [])).strip()
                    if text:
                        segs.append(f"- {text}")
                else:
                    text = extract_text_recursive([c]).strip()
                    if text:
                        segs.append(text)
            elif isinstance(c, str):
                segs.append(c)
        return segs

    def render_list(node):
        items = []
        for li in node.get("children", []):
            if li.get("type") == "li":
                txt = extract_text_recursive(li.get("children", [])).strip()
                if txt:
                    items.append(f"- {txt}")
        return "\n".join(items)

    for v in value:
        if v.get("type") in ("ul", "ol"):
            parts.append(render_list(v))
        else:
            children_texts = render_children(v.get("children", []))
            if children_texts:
                parts.append(" ".join(children_texts).strip())

    return "\n".join(p for p in parts if p)


def find_section_range(blocks, items, start_title, end_title=None):
    start_idx = next(
        (
            i
            for i, bid in enumerate(items)
            if start_title.strip().lower()
            in (blocks.get(bid, {}).get("plaintext") or "").strip().lower()
        ),
        None,
    )
    if start_idx is None or not is_h3_block(blocks.get(items[start_idx], {})):
        return None, None

    end_idx = None
    if end_title:
        end_idx = next(
            (
                i
                for i, bid in enumerate(items)
                if end_title.strip().lower()
                in (blocks.get(bid, {}).get("plaintext") or "").strip().lower()
            ),
            None,
        )

    if end_idx is None:
        for i in range(start_idx + 1, len(items)):
            if is_h3_block(blocks.get(items[i], {})):
                end_idx = i
                break

    return start_idx, end_idx


def extract_section_text(blocks, items, start_title, end_title=None):
    """Extract text between two h3 headings from Slate blocks."""
    start_idx, end_idx = find_section_range(blocks, items, start_title, end_title)
    if start_idx is None:
        return ""

    content_slice = items[start_idx + 1:end_idx] if end_idx else items[start_idx + 1:]
    parts = []

    for bid in content_slice:
        block = blocks.get(bid, {})
        if block.get("@type") != "slate":
            continue
        if is_h3_block(block):
            break

        text = render_slate_value(block.get("value", [])) or block.get("plaintext", "")
        text = text.strip()
        if text:
            parts.append(text.rstrip("."))

    return "\n".join(p.strip().rstrip('.') for p in parts if p.strip())


def richtext_to_plain_text(value):
    if isinstance(value, dict) and "data" in value:
        html = value.get("data", "")
        return html_to_plain_text(html, inline_links=False)
    return value
