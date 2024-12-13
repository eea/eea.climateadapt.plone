import json
import argparse


def filter_localroles(input_file, output_file, blacklist):
    """
    Reads JSON data from the input file, removes keys in the blacklist from the `localroles` object,
    and writes the filtered data to the output file.

    :param input_file: Path to the input JSON file
    :param output_file: Path to the output JSON file
    :param blacklist: List of keys to be removed from `localroles`
    """
    try:
        # Read the input JSON file
        with open(input_file, "r") as infile:
            data = json.load(infile)

        # Process the JSON data
        filtered_data = []
        for item in data:
            if "localroles" in item:
                # Remove blacklisted keys
                item["localroles"] = {
                    key: roles
                    for key, roles in item["localroles"].items()
                    if key not in blacklist
                }

                # Skip the item if `localroles` is empty
                if not item["localroles"]:
                    continue

            filtered_data.append(item)

        # Write the filtered data to the output JSON file
        with open(output_file, "w") as outfile:
            json.dump(filtered_data, outfile, indent=4)

        print(f"Filtered data written to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Filter keys from 'localroles' in a JSON file."
    )
    parser.add_argument("input_file", type=str, help="Path to the input JSON file")
    parser.add_argument("output_file", type=str, help="Path to the output JSON file")
    parser.add_argument(
        "--blacklist",
        type=str,
        nargs="+",
        default=[
            "tibi",
            "tiberich",
            "tripodor",
            "iulianpetchesi",
            "ghitab",
            "eugentripon",
            "krisztina",
            "ghicaale",
            "tibiadmin",
            "iuliantest",
        ],
        help="Keys to be removed from 'localroles' (default: ['tibi'])",
    )

    args = parser.parse_args()

    # Execute the function
    filter_localroles(args.input_file, args.output_file, args.blacklist)
