#!/bin/env python3
from datetime import datetime
import json
import os
import sys
import time
from typing import Callable, List


def fix_storage_type(obj):
    """Fixes 'storage_type' field: sets to None if its value is 'NONE'."""
    if obj.get("storage_type") == "NONE":
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


fixers: List[Callable[[dict], dict]] = [
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

    foldername = sys.argv[1]

    start_time = time.time()  # Start the timer

    try:
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
            print(f"Processing file {index}/{total_files}: {filename}")

            try:
                # Open and load the JSON file
                with open(filename, "r") as file:
                    data = json.load(file)

                # Ensure the file contains an object
                if not isinstance(data, dict):
                    print(
                        f"Skipping file '{filename}': JSON file must contain a single object."
                    )
                    continue

                # Apply each fixer to the object
                for fixer in fixers:
                    data = fixer(data)

                # Write the fixed data back to the file
                with open(filename, "w") as file:
                    json.dump(data, file, indent=4)

                print(f"File '{filename}' has been processed successfully.")

            except json.JSONDecodeError:
                import pdb

                pdb.set_trace()
                print(f"Error: File '{filename}' is not a valid JSON file.")
            except Exception as e:
                if filename != "errors.json":
                    import pdb

                    pdb.set_trace()
                    print(
                        f"An unexpected error occurred while processing '{filename}': {e}"
                    )

        end_time = time.time()  # End the timer
        duration = end_time - start_time
        print(f"All files processed in {duration:.2f} seconds.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
