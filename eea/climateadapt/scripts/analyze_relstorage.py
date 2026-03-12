"""Raw RelStorage Analyzer (zodb analyze alternative)"""

import argparse
import sys
from collections import Counter
from Zope2.Startup.options import ZopeWSGIOptions
from ZODB.utils import get_pickle_metadata

parser = argparse.ArgumentParser(
    description="Analyze raw RelStorage object counts and sizes."
)
parser.add_argument(
    "--zope-conf", required=True, help="Path to zope.conf or relstorage.conf"
)


def main():
    args = parser.parse_args()

    # Use ZopeWSGIOptions to parse the config file correctly
    # This handles the Zope schema, environment variables, conditional imports, etc.
    options = ZopeWSGIOptions(args.zope_conf)()
    
    # Get the first database from the configuration
    storage = options.configroot.databases[0].config.storage.open()

    class_counts = Counter()
    class_sizes = Counter()

    print("Scanning RelStorage... this will take a moment.")

    # Iterate through all transactions and records in the database
    try:
        for tx in storage.iterator():
            for record in tx:
                # The class name is stored in the first few bytes of the pickled data
                try:
                    mod, klass = get_pickle_metadata(record.data)
                    full_class = f"{mod}.{klass}"
                except Exception:
                    full_class = "Unknown"

                size = len(record.data or b"")
                class_counts[full_class] += 1
                class_sizes[full_class] += size
    finally:
        storage.close()

    print(f"\n{'CLASS':<60} | {'COUNT':<10} | {'TSIZE (MB)':<10} | {'AVG SIZE (B)'}")
    print("-" * 100)

    # Sort by total size descending
    for cls, count in class_sizes.most_common():
        tsize_mb = count / (1024 * 1024)
        avg_size = count / class_counts[cls]
        print(
            f"{cls:<60} | {class_counts[cls]:<10} | {tsize_mb:<10.2f} | {avg_size:<10.0f}"
        )


if __name__ == "__main__":
    main()
