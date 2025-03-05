#!/bin/env python3
import json
import os
import sys
import time
import logging

logger = logging.getLogger("fixer")


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

_storagetypes = [
    "PLAINMETADATA",
    "PROJECT",
    "MAPLAYER",
    "URL",
    "SETOFMAPS",
    "MEASURE",
]

def main():
    # Read the folder name from command line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <foldername>")
        sys.exit(1)
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

    storage_types = set()
    data_types = set()

    for index, filename in enumerate(json_files, start=1):

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

        # Extract storage_type and data_type if present
        file_storage_type = data.get("storage_type")
        file_data_type = data.get("data_type")

        if file_storage_type and file_storage_type not in _storagetypes:
            storage_types.add(file_storage_type)

        if file_data_type and file_data_type not in _datatypes:
            data_types.add(file_data_type)


        print(f"File '{filename}' has been processed successfully.")

    # Display results
    print("Storage Types not in _storagetypes:", storage_types)
    print("Data Types not in _datatypes:", data_types)

    end_time = time.time()  # End the timer
    duration = end_time - start_time
    print(f"All files processed in {duration:.2f} seconds.")

    # try:
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
