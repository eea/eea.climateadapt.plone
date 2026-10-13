"""CLI entry point for assigning Extended Tool categories from ODS."""

import argparse
import logging
import os
import sys
from collections import Counter

from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.tool_type_import import (
    DEFAULT_TARGET_PATH,
    ToolTypeAssignmentError,
    ToolTypeImporter,
    parse_assignment_ods,
)


logger = logging.getLogger("eea.climateadapt.importer.tool_types")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def main():
    parser = argparse.ArgumentParser(
        description="Assign Extended Tool categories from an ODS spreadsheet."
    )
    parser.add_argument("--file", required=True, help="Path to the assignment ODS file")
    parser.add_argument(
        "--commit",
        action="store_true",
        default=False,
        help="Commit changes to the database (default is dry-run)",
    )
    parser.add_argument("--portal", default="cca", help="Portal ID (default: cca)")
    parser.add_argument(
        "--target-path",
        default=DEFAULT_TARGET_PATH,
        help=f"Extended Tools folder (default: {DEFAULT_TARGET_PATH})",
    )
    parser.add_argument(
        "--zope-conf",
        default="/app/etc/relstorage.conf",
        help="Path to zope.conf or relstorage.conf",
    )
    args = parser.parse_args()

    file_path = os.path.abspath(args.file)
    if not os.path.exists(file_path):
        logger.error("Assignment file not found: %s", file_path)
        return 2

    try:
        assignments = parse_assignment_ods(file_path)
    except (OSError, ToolTypeAssignmentError) as error:
        logger.error("Invalid assignment file: %s", error)
        return 2

    logger.info("Validated %d tool-type assignments", len(assignments))
    site = get_plone_site(zope_conf=args.zope_conf, portal_id=args.portal)
    importer = ToolTypeImporter()
    try:
        results = importer.import_assignments(
            site,
            assignments,
            dry_run=not args.commit,
            container=args.target_path,
        )
    except (RuntimeError, ToolTypeAssignmentError) as error:
        logger.error("Import failed: %s", error)
        return 2

    for result in results:
        print(
            f"[{result['status']:12s}] {result['external_id']:6s} "
            f"{result['category']} - {result.get('actual_name', result['name'])}"
        )

    counts = Counter(result["status"] for result in results)
    summary = ", ".join(
        f"{key}={value}" for key, value in sorted(counts.items())
    )
    print(f"\nSummary: {summary}")
    if not args.commit:
        print("DRY-RUN complete; pass --commit to write the assignments.")

    return 1 if counts.get("NOT_FOUND") else 0


if __name__ == "__main__":
    sys.exit(main())
