#!/bin/env python3
from datetime import datetime
import ast
import json
import os
import sys
import time
from typing import Callable, List
import logging

logger = logging.getLogger("fixer")

REPLACED_URL = 'https://climate-adapt.eea.europa.eu/_admin'
REPLACE_WITH = 'https://climate-adapt-plone6.devel5cph.eea.europa.eu'
START_FROM = 0

def get_blocks(obj):
    """get_blocks"""

    blocks_layout = obj.get("blocks_layout", {})
    order = blocks_layout.get("items", [])
    blocks = obj.get("blocks", {})

    out = []
    for _id in order:
        if _id not in blocks:
            continue
        out.append((_id, blocks[_id]))

    return out


class BlocksTraverser(object):
    """BlocksTraverser"""

    def __init__(self, context):
        self.context = context

    def __call__(self, visitor):
        for _, block_value in get_blocks(self.context):
            # if visitor(block_value):
            #     self.context._p_changed = True

            self.handle_subblocks(block_value, visitor)

    def handle_subblocks(self, block_value, visitor):
        """handle_subblocks"""

        if (
            "data" in block_value
            and isinstance(block_value["data"], dict)
            and "blocks" in block_value["data"]
        ):
            for block in list(block_value["data"]["blocks"].values()):
                visitor(block)

                self.handle_subblocks(block, visitor)

        if "blocks" in block_value:
            for block in list(block_value["blocks"].values()):
                visitor(block)

                self.handle_subblocks(block, visitor)

        if "columns" in block_value:
            for block in list(block_value["columns"]):
                visitor(block)
                self.handle_subblocks(block, visitor)


cca_url = "https://climate-adapt.eea.europa.eu"

href_url_fields = ["@id", "getURL"]


def fix_marker_interfaces(obj):
    """ add marker interfaces for the specified content types """
    _type = obj.get("@type")
    marker_interfaces = {
        "collective.cover.content": "eea.climateadapt.interfaces.ICover",
        "Subsite": "plone.base.interfaces.siteroot.INavigationRoot"
    }

    if not _type:
        import pdb
        pdb.set_trace()

    if _type == "Folder" and obj["@id"].endswith("/observatory"):
        obj["@type"] = _type = "Subsite"

    if _type in marker_interfaces:
        interface_to_add = marker_interfaces[_type]
        if "exportimport.marker_interfaces" in obj:
            if interface_to_add not in obj["exportimport.marker_interfaces"]:
                obj["exportimport.marker_interfaces"].append(interface_to_add)
        else:
            obj["exportimport.marker_interfaces"] = [interface_to_add]

    return obj

def fix_url(value):
    if isinstance(value, list):
        import pdb

        pdb.set_trace()
    else:
        return value.replace(cca_url, "")


def _fix_teaser_internal_link(block):
    if block.get("@type") == "teaser":
        extras = []
        if block.get("preview_image"):
            if isinstance(block["preview_image"], str):
                block["preview_image"] = fix_url(block["preview_image"])
            else:
                extras = block["preview_image"]

        for href in block.get("href", []) + extras:
            for name in href_url_fields:
                base_id = href.get(name)
                if base_id and cca_url in base_id:
                    href[name] = fix_url(base_id)
                    logger.info("Fixed teaser href url: (%s) %s", name, base_id)


block_fixers = [_fix_teaser_internal_link]


def traverse_blocks(obj):
    traverser = BlocksTraverser(obj)
    for visitor in block_fixers:
        traverser(visitor)
    return obj


def fix_storage_type(obj):
    """Fixes 'storage_type' field: sets to None if its value is 'NONE'."""
    none_types = ['BRAK', 'NINGUNA', 'KEINE', 'NESSUNA', 'AUCUN', 'NONE']

    if obj.get("storage_type") in none_types:
        obj["storage_type"] = None
    return obj


def fix_missing_field_values(obj):
    fields = [
        "publication_date",
        "geochars",
        "sectors",
        "climate_impacts",
        "overview_app_toolbox_url",
        "overview_app_parameters",
        "websites",
        "keywords",
        "health_impacts",
        "funding_programme",
        "relevance",
        "implementation_type",
        "overview_app_ecde_identifier",
        "subsite_css_class",
        "event_url",
        "title",
        "long_description",
        "acronym",
        "challenges",
        "lead",
        "partners",
        "objectives",
        "category",
        "solutions",
        "file",
        "image",
        "embed_url",
        "start",
        "end",
    ]
    for field in fields:
        if field in obj and not obj[field]:
            del obj[field]
    return obj


def fix_exclude_from_nav(obj):
    """for covers set exclude_from_nav to True because they are excluded from navigation"""
    if obj.get("@type") == "collective.cover.content":
        obj["exclude_from_nav"] = True

    return obj


def fix_health_impacts(obj):
    replaced = {
        "Floods and storms": "Droughts and floods",
        "Infectious diseases": "Climate-sensitive diseases",
        "Heat and cold": "Heat",
        "Air quality and aeroallergens": "Air pollution and aero-allergens",
        # "SOCIETALASP": ""
    }
    removed = []
    if obj.get("health_impacts"):
        obj["health_impacts"] = [x for x in obj["health_impacts"] if x not in removed]
        obj["health_impacts"] = [replaced.get(x, x) for x in obj["health_impacts"]]

    return obj


def fix_elements(obj):
    replaced = {
        # "SOCIETALASP": ""
    }
    _type = obj.get("@type")
    if _type != "eea.climateadapt.casestudy":
        removed = ["SOCIETALASP", "COSTBENEFIT", "ECONOMICASP"]
        if obj.get("elements"):
            obj["elements"] = [x for x in obj["elements"] if x not in removed]
            obj["elements"] = [replaced.get(x, x) for x in obj["elements"]]

    return obj


def fix_keywords(obj):
    if obj.get("keywords"):
        # this splits the keywords by '\n' in cases like
        # "Vegetation\nClimate change \nFire"
        obj["keywords"] = [
            keyword.strip()
            for entry in obj["keywords"]
            for keyword in entry.split("\n")
        ]
        obj["keywords"] = [k.strip() for k in obj["keywords"] if k.strip()]

    return obj


def _fix_invalid_url(url):
    url = url.replace("\n", " ")
    url = url.replace("\r", " ")
    return url

    if url.startswith("www."):
        url = "https://" + url

    if not url.startswith("http"):
        url = "https://www." + url

    return url


def fix_websites(obj):
    if obj.get("websites"):
        obj["websites"] = [
            _fix_invalid_url(k.strip()) for k in obj["websites"] if k.strip()
        ]
    return obj


def fix_special_tags(obj):
    if obj.get("special_tags"):
        obj["special_tags"] = [k for k in obj["special_tags"] if k.strip()]
    return obj


def fix_sectors(obj):
    replaced = {
        # "SOCIETALASP": ""
    }
    removed = ["ECOSYSTEM"]
    if obj.get("sectors"):
        obj["sectors"] = [x for x in obj["sectors"] if x not in removed]
        obj["sectors"] = [replaced.get(x, x) for x in obj["sectors"]]

    return obj


def fix_attendees(obj):
    if obj.get("attendees"):
        obj["attendees"] = [k for k in obj["attendees"] if k.strip()]
    return obj


def fix_origin_website(obj):
    replaced = {
        # "SOCIETALASP": ""
    }
    removed = ["Climate-ADAPT"]
    if obj.get("origin_website"):
        obj["origin_website"] = [x for x in obj["origin_website"] if x not in removed]
        obj["origin_website"] = [replaced.get(x, x) for x in obj["origin_website"]]

    return obj


def fix_titles(obj):
    if obj.get("title"):
        obj["title"] = obj["title"].replace("\n", " ")
    return obj


def fix_spatial_layer(obj):
    if obj.get("spatial_layer") and isinstance(obj["spatial_layer"], (list, tuple)):
        obj["spatial_layer"] = ", ".join(obj["spatial_layer"])

    return obj


def fix_content_types(obj):
    _type = obj.get("@type")
    remapped = {"collective.cover.content": "Folder"}

    if "unexported_paths" in obj:
        return

    if not _type:
        import pdb

        pdb.set_trace()

    if _type in remapped:
        obj["@type"] = remapped[_type]

    return obj


# def fix_relevance(obj):
#     if 'relevance' in obj and not obj['relevance']:


def fix_publishing_date(obj):
    """fix objects with publication_date(effective) being after expiration date(expires)"""
    if obj.get("effective") and obj.get("expires"):
        expiration_date = datetime.strptime(obj["expires"], "%Y-%m-%dT%H:%M:%S")
        publication_date = datetime.strptime(obj["effective"], "%Y-%m-%dT%H:%M:%S")

        if publication_date > expiration_date:
            obj["effective"] = obj["expires"]

    return obj

_datatypes = [
    "DOCUMENT",
    "INFORMATIONSOURCE",
    "MAPGRAPHDATASET",
    "INDICATOR",
    "GUIDANCE",
    "TOOL",
    "RESEARCHPROJECT",
    "MEASURE",
    "ACTION",
    "ORGANISATION",
    # "VIDEOS",
]

def fix_data_type(obj):
    replaced = {
        "DOCUMENTO": "DOCUMENT",
        "SCHRIFTSTÜCK": "DOCUMENT",
        "DOKUMENT": "DOCUMENT",
        "WERKZEUG": "TOOL",
        "ORIENTACIONES": "GUIDANCE",
        "INDICADOR": "INDICATOR",
        "ORGANIZACIÓN": "ORGANISATION",
        "INFORMACIÓN": "INFORMATIONSOURCE",
        "HERRAMIENTA": "TOOL",
        "ORIENTATIONS": "GUIDANCE",
        "UN DOCUMENT": "DOCUMENT",
        "OUTIL": "TOOL",
        "ORIENTAMENTI": "GUIDANCE",
        "INDICATORE": "INDICATOR",
        "INDICATEUR": "INDICATOR",
        "WSKAŹNIK": "INDICATOR",
        "ORGANIZZAZIONE": "ORGANISATION",
        "STRUMENTO": "TOOL",
        "WYTYCZNE": "GUIDANCE",
        "ORGANIZACJA": "ORGANISATION",
        "INFORMACJE TRYBUNAŁU": "INFORMATIONSOURCE",
        "INFORMACJA": "INFORMATIONSOURCE",
        "KOMISJI": "ORGANISATION",
        "NARZĘDZIE": "TOOL",
        "LEITLINIEN": "GUIDANCE",
        "INDIKATOR": "INDICATOR",
        "ORGANISATION, EINRICHTUNG": "ORGANISATION",
    }
    data_type = obj.get("data_type", None)

    if data_type and data_type not in _datatypes:
        if data_type not in replaced:
            import pdb; pdb.set_trace()
        obj["data_type"] = replaced.get(data_type, data_type)

    return obj

fixers: List[Callable[[dict], dict]] = [
    fix_marker_interfaces,
    fix_exclude_from_nav,
    fix_storage_type,
    fix_missing_field_values,
    fix_elements,
    fix_sectors,
    fix_health_impacts,
    fix_keywords,
    fix_titles,
    fix_origin_website,
    fix_special_tags,
    fix_websites,
    fix_spatial_layer,
    fix_content_types,
    fix_attendees,
    fix_publishing_date,
    fix_data_type,
    traverse_blocks,
]


def main_single_file():
    # Read the file name from command line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        # Open and load the JSON file
        with open(filename, "r") as file:
            data = json.load(file)

        # Ensure the file contains an array of objects
        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array of objects.")

        # Define fixers as a list of functions
        # Apply each fixer to every object in the array
        fixed_data = []

        if REPLACED_URL in str(data):
            data_str = str(data).replace(REPLACED_URL, REPLACE_WITH)
            data = ast.literal_eval(data_str)

        for obj in data:
            if "unexported_paths" in obj:
                print(f"There are unexported_paths: \n, {obj['unexported_paths']}")
                continue

            for fixer in fixers:
                obj = fixer(obj)

            fixed_data.append(obj)

        # Write the fixed data back to the file
        with open(filename, "w") as file:
            json.dump(fixed_data, file, indent=4)

        print(f"File '{filename}' has been processed successfully.")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    # Read the folder name from command line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <foldername>")
        sys.exit(1)
    skip_types = ["DepictionTool", "PDFTool", "PDFTheme", "ProgressTool",
                  "VocabularyLibrary"]
    foldername = sys.argv[1]

    start_time = time.time()  # Start the timer

    # Ensure the folder exists
    if not os.path.isdir(foldername):
        raise ValueError(f"'{foldername}' is not a valid folder.")

    # Get all JSON files in the folder
    json_files = [
        os.path.join(foldername, file)
        for file in os.listdir(foldername)
        if file.endswith(".json")
    ]

    total_files = len(json_files)

    if total_files == 0:
        print(f"No JSON files found in folder '{foldername}'.")
        return

    for index, filename in enumerate(json_files, start=1):
        if index < START_FROM:
            continue

        print(f"Processing file {index}/{total_files}: {filename}")

        # Open and load the JSON file
        with open(filename, "r") as file:
            data = json.load(file)

        # Ensure the file contains an object
        if not isinstance(data, dict):
            print(
                f"Skipping file '{filename}': JSON file must contain a single object."
            )
            continue

        if data['@type'] in skip_types:
            os.remove(filename)
            print(f"File '{filename}' has been DELETED.")
            continue

        if REPLACED_URL in str(data):
            data_str = str(data).replace(REPLACED_URL, REPLACE_WITH)
            data = ast.literal_eval(data_str)

        for fixer in fixers:
            data = fixer(data)

        # Write the fixed data back to the file
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        print(f"File '{filename}' has been processed successfully.")

        # try:
        #
        #     # Apply each fixer to the object
        #     for fixer in fixers:
        #         data = fixer(data)
        # except json.JSONDecodeError:
        #     import pdb
        #
        #     pdb.set_trace()
        #     print(f"Error: File '{filename}' is not a valid JSON file.")
        # except Exception as e:
        #     if not filename.endswith("errors.json"):
        #         import pdb
        #
        #         pdb.set_trace()
        #         print(
        #             f"An unexpected error occurred while processing '{filename}': {e}"
        #         )

    end_time = time.time()  # End the timer
    duration = end_time - start_time
    print(f"All files processed in {duration:.2f} seconds.")

    # try:
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
