"""CLI entry point for importing extended tools from ODS spreadsheets into Climate-ADAPT.

Usage:
  import_extended_tools --file1 <path> --file2 <path> [--commit]
"""

import argparse
import logging
import os
import sys

from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.tool_import import ExtendedToolsImporter, parse_ods_rows

logger = logging.getLogger("eea.climateadapt.importer.extended_tools")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def main():
    """CLI entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        description="Import extended tools from ODS spreadsheets into Climate-ADAPT."
    )
    parser.add_argument(
        "--file1",
        dest="file1",
        default="/app/sources/eea.climateadapt/data/tools_main.ods",
        help="Path to main metadata ODS file",
    )
    parser.add_argument(
        "--file2",
        dest="file2",
        default="/app/sources/eea.climateadapt/data/tools_extra.ods",
        help="Path to extra fields ODS file",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        default=False,
        help="Commit changes to database (default is dry-run)",
    )
    parser.add_argument(
        "--portal",
        dest="portal_id",
        default="cca",
        help="Portal ID (default: cca)",
    )
    parser.add_argument(
        "--target-path",
        dest="target_path",
        default=None,
        help="Target folder path for import (default: /cca/en/metadata/tools)",
    )
    parser.add_argument(
        "--zope-conf",
        dest="zope_conf",
        default="/app/etc/relstorage.conf",
        help="Path to zope.conf or relstorage.conf",
    )

    args = parser.parse_args()

    file1_path = os.path.abspath(args.file1)
    file2_path = os.path.abspath(args.file2) if args.file2 else None

    if not os.path.exists(file1_path):
        logger.error("File 1 not found: %s", file1_path)
        sys.exit(1)
    if file2_path and not os.path.exists(file2_path):
        logger.warning("File 2 not found: %s (will import File 1 only)", file2_path)
        file2_path = None

    site = get_plone_site(zope_conf=args.zope_conf, portal_id=args.portal_id)

    importer = ExtendedToolsImporter()
    logger.info("Parsing File 1: %s", file1_path)
    rows1 = parse_ods_rows(file1_path)
    tools1 = importer.parse_file1_rows(rows1)
    logger.info("Found %d tools in File 1", len(tools1))

    tools2 = {}
    if file2_path:
        logger.info("Parsing File 2: %s", file2_path)
        rows2 = parse_ods_rows(file2_path)
        tools2 = importer.parse_file2_rows(rows2)
        logger.info("Found %d tools in File 2", len(tools2))

    merged = importer.merge_datasets(tools1, tools2)
    logger.info("Merged total: %d unique tools", len(merged))

    results = importer.import_tools(
        site, merged, dry_run=not args.commit, container=args.target_path
    )

    for r in results:
        extra_info = ""
        if "inputs" in r:
            extra_info = (
                f" [in:{r['inputs']} out:{r['outputs']} use:{r['use_it_to']} "
                f"rel:{1 if r['relevance'] else 0} used_in:{r['used_in']}]"
            )
        print(
            f"[{r['status']:7s}] {r['external_id']:6s} - {r['name'][:40]:40s} {extra_info}"
        )

    if not args.commit:
        print(
            "\n*** DRY-RUN COMPLETE (no changes committed). Pass --commit to write to ZODB. ***"
        )
    else:
        print("\n*** SUCCESS: All changes committed to ZODB. ***")


if __name__ == "__main__":
    main()
