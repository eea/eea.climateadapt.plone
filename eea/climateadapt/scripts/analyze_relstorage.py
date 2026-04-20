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

    total_size = sum(class_sizes.values())
    total_count = sum(class_counts.values())

    # Find the maximum class name length for dynamic column sizing
    max_class_len = max([len(cls) for cls in class_sizes.keys()] + [len("CLASS")])
    # Cap it at a reasonable width for terminal display but allow it to grow if needed
    col_width = min(max_class_len, 100)

    header = (
        f"{'CLASS':<{col_width}} | "
        f"{'COUNT':>12} | "
        f"{'TSIZE (MB)':>12} | "
        f"{'PERCENT':>8} | "
        f"{'AVG (B)':>10}"
    )
    print(f"\n{header}")
    print("-" * len(header))

    # Sort by total size descending
    for cls, size in class_sizes.most_common():
        count = class_counts[cls]
        tsize_mb = size / (1024 * 1024)
        percent = (size / total_size * 100) if total_size > 0 else 0
        avg_size = size / count if count > 0 else 0

        # Truncate class name if it's still too long for col_width
        display_cls = (cls[: col_width - 3] + "...") if len(cls) > col_width else cls

        print(
            f"{display_cls:<{col_width}} | "
            f"{count:>12,.0f} | "
            f"{tsize_mb:>12.2f} | "
            f"{percent:>7.1f}% | "
            f"{avg_size:>10,.0f}"
        )

    print("-" * len(header))
    print(
        f"{'TOTAL':<{col_width}} | "
        f"{total_count:>12,.0f} | "
        f"{total_size / (1024 * 1024):>12.2f} | "
        f"{'100.0%':>8} | "
        f"{total_size / total_count if total_count > 0 else 0:>10,.0f}"
    )


if __name__ == "__main__":
    main()
