"""EXPLORATION ONLY: classify internal references found in blocks of the
(old) /en/mission subtree and guess what happened to their targets.

    docker compose exec backend /app/docker-entrypoint.sh \
        /app/bin/python3 -m eea.climateadapt.scripts.analyze_mission_refs \
        --portal cca --zope-conf etc/relstorage.conf
"""

import argparse
import collections
import csv
import re
import sys
from urllib.parse import urlparse

from plone import api
from plone.restapi.blocks import visit_blocks

from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.scripts.scan_block_links import classify, walk_block

RU = re.compile(r"resolveuid/([a-fA-F0-9\-]+)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portal", dest="portal_id", required=True)
    ap.add_argument("--zope-conf", dest="zope_conf", required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--csv", default="")
    args = ap.parse_args()

    site = get_plone_site(args.zope_conf, args.portal_id)
    portal_path = "/".join(site.getPhysicalPath())
    catalog = api.portal.get_tool("portal_catalog")

    recent = catalog(portal_type="Folder", sort_on="modified", sort_order="reverse")[:3]
    for b in recent:
        print("newest:", b.modified, b.getPath(), flush=True)

    old_root = f"{portal_path}/{args.lang}/mission"
    brains = catalog(path={"query": old_root})
    print(f"objects under {old_root}: {len(brains)}", flush=True)

    uid_cache = {}

    def uid_to_path(uid):
        if uid not in uid_cache:
            found = catalog(UID=uid)
            uid_cache[uid] = found[0].getPath() if found else None
        return uid_cache[uid]

    rows = []
    kinds = collections.Counter()
    targets = collections.Counter()

    for brain in brains:
        try:
            obj = brain.getObject()
            blocks = getattr(obj, "blocks", None)
            if not isinstance(blocks, dict) or not blocks:
                continue
            for block in visit_blocks(obj, blocks):
                if not isinstance(block, dict):
                    continue
                btype = block.get("@type")
                for field, value in walk_block(block):
                    cls = classify(value)
                    if cls is None:
                        continue
                    kind, key, raw = cls
                    if kind == "external-host":
                        continue
                    target = None
                    if kind == "resolveuid":
                        target = uid_to_path(key)
                    elif kind == "absolute-internal":
                        target = f"{portal_path}{urlparse(raw).path}"
                    elif kind == "root-relative":
                        target = f"{portal_path}{raw}"
                    if not target:
                        continue
                    rel = target[len(portal_path) :]
                    segs = [s for s in rel.split("/") if s]
                    section = "/".join(segs[1:3]) if len(segs) > 2 else "/".join(segs)
                    kinds[(btype, field, kind)] += 1
                    targets[section] += 1
                    rows.append(
                        {
                            "object": brain.getPath(),
                            "block_type": btype,
                            "field": field,
                            "kind": kind,
                            "value": raw,
                            "target": target,
                            "target_section": section,
                        }
                    )
        except Exception as exc:  # noqa: BLE001
            print("ERROR", brain.getPath(), exc, flush=True)

    print(f"\ninternal refs found: {len(rows)}")
    print("\n--- target section (2 levels below language root) ---")
    for k, v in targets.most_common(40):
        print(f"  {k:60} {v}")
    print("\n--- (block_type, field, kind) ---")
    for (btype, field, kind), v in kinds.most_common(40):
        print(f"  {str(btype):24} {field:36} {kind:18} {v}")

    missing = [r for r in rows if r["kind"] == "resolveuid" and not r["target"]]
    print(f"\nresolveuid refs whose UID is NOT in local catalog: {len(missing)}")

    if args.csv:
        with open(args.csv, "w", newline="") as fp:
            w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
