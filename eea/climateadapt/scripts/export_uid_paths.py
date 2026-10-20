"""Export a UID -> path dictionary (and an optional block-join dictionary) from
a database that still has the *pre-reorganisation* content.

Run this against the old/pre-reorg database (for the Climate-ADAPT mission
reorganisation that means a database where ``/en/mission`` is still the real
subsite). The resulting JSON files are consumed by ``fix_mission_block_links``
which runs on the reorganised database.

    docker compose exec backend /app/docker-entrypoint.sh \
        bin/export_uid_paths --portal cca --zope-conf etc/relstorage.conf \
        --out /app/import/mission_uid_paths.json \
        --block-join /app/import/mission_block_join.json
"""

import argparse
import json
import logging
import sys

from plone import api
from plone.app.multilingual.interfaces import ILanguageRootFolder

from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.scripts._blocks import (
    ABSOLUTE_INTERNAL,
    RESOLVEUID,
    ROOT_RELATIVE,
    classify,
    iter_blocks,
    iter_strings,
)

logger = logging.getLogger("fixer")

INTERNAL_HOSTS = (
    "climate-adapt.eea.europa.eu",
    "demo-climate-adapt.02pre.eea.europa.eu",
)


def language_roots(site):
    for _id, child in site.items():
        if ILanguageRootFolder.providedBy(child):
            yield child.getId()


def collect(site, paths, include_all):
    catalog = api.portal.get_tool("portal_catalog")
    portal_path = "/".join(site.getPhysicalPath())

    queries = []
    if include_all:
        queries.append({"query": portal_path})
    else:
        for path in paths:
            if "*" in path:
                for lang in language_roots(site):
                    queries.append(
                        {
                            "query": f"{portal_path}/{path.replace('*', lang)}".rstrip(
                                "/"
                            )
                        }
                    )
            else:
                queries.append({"query": f"{portal_path}/{path.strip('/')}"})

    brains = []
    seen = set()
    for query in queries:
        found = catalog(path=query)
        logger.info("%s -> %s objects", query["query"], len(found))
        for brain in found:
            if brain.UID not in seen:
                seen.add(brain.UID)
                brains.append(brain)
    return brains


def main():
    parser = argparse.ArgumentParser(prog="export_uid_paths")
    parser.add_argument("--portal", dest="portal_id", required=True, help="Portal ID")
    parser.add_argument(
        "--zope-conf", dest="zope_conf", required=True, help="Path to zope.conf"
    )
    parser.add_argument(
        "--path",
        dest="paths",
        action="append",
        default=[],
        metavar="PATH",
        help="Portal-relative path to export; '*' is the language code. "
        "May be repeated. Default: /*/mission",
    )
    parser.add_argument(
        "--all", action="store_true", help="Export every catalog brain (large)"
    )
    parser.add_argument("--out", dest="out", required=True, help="Output JSON file")
    parser.add_argument(
        "--block-join",
        dest="block_join",
        default="",
        help="Also dump a per-object block reference map to this JSON file",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Log every object being scanned"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    site = get_plone_site(args.zope_conf, args.portal_id)
    portal_path = "/".join(site.getPhysicalPath())
    paths = args.paths or ["/*/mission"]

    brains = collect(site, paths, args.all)
    logger.info("Collected %s brains", len(brains))

    uid_paths = {}
    block_join = {}
    catalog = api.portal.get_tool("portal_catalog")
    extra_uid_paths = {}

    def lookup(uid):
        """Resolve a UID that lives outside the exported subtree (cached)."""
        if uid not in extra_uid_paths:
            found = catalog(UID=uid)
            extra_uid_paths[uid] = (
                found[0].getPath()[len(portal_path) :] if found else ""
            )
        return extra_uid_paths[uid] or None

    for index, brain in enumerate(brains):
        try:
            rel = brain.getPath()[len(portal_path) :]
            uid_paths[brain.UID] = rel
            if not args.block_join:
                continue
            obj = brain.getObject()
            if not getattr(obj, "blocks", None):
                continue
            entries = []
            for bid, block, container in iter_blocks(obj):
                for _container, _key, field, value in iter_strings(block):
                    kind, key = classify(value, INTERNAL_HOSTS)
                    if kind == RESOLVEUID:
                        target = uid_paths.get(key) or lookup(key)
                    elif kind in (ABSOLUTE_INTERNAL, ROOT_RELATIVE):
                        target = key
                    else:
                        continue
                    if target:
                        entries.append(
                            {
                                "block_id": bid,
                                "container": container,
                                "field": field,
                                "block_type": block.get("@type"),
                                "target": target,
                            }
                        )
            if entries:
                block_join[rel] = entries
            if args.verbose and index % 200 == 0:
                logger.info("... %s/%s", index, len(brains))
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed on %s: %s", brain.getPath(), exc)

    with open(args.out, "w") as fp:
        json.dump(uid_paths, fp, indent=1, sort_keys=True)
    logger.info("Wrote %s entries to %s", len(uid_paths), args.out)

    if args.block_join:
        with open(args.block_join, "w") as fp:
            json.dump(block_join, fp, indent=1, sort_keys=True)
        logger.info("Wrote %s objects to %s", len(block_join), args.block_join)

    return 0


if __name__ == "__main__":
    sys.exit(main())
