#!/bin/env python3
import json
import sys
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
    ]
    for field in fields:
        if field in obj and not obj[field]:
            del obj[field]
    return obj


def fix_elements(obj):
    replaced = {
        # "SOCIETALASP": ""
    }
    removed = ["SOCIETALASP"]
    if obj.get("elements"):
        obj["elements"] = [x for x in obj["elements"] if x not in removed]
        obj["elements"] = [replaced.get(x, x) for x in obj["elements"]]

    return obj


fixers: List[Callable[[dict], dict]] = [
    fix_storage_type,
    fix_missing_field_values,
    fix_elements,
]


def main():
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
        for obj in data:
            for fixer in fixers:
                obj = fixer(obj)

        # Write the fixed data back to the file
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        print(f"File '{filename}' has been processed successfully.")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
