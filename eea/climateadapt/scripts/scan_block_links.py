"""EXPLORATION ONLY: scan Volto blocks for internal links and report their shape.

Read-only. Run inside the backend container:

    docker compose exec backend /app/docker-entrypoint.sh \
        /app/bin/python3 -m eea.climateadapt.scripts.scan_block_links \
        --portal cca --zope-conf etc/relstorage.conf --path /en/mission
"""

import argparse
import json
import re
import sys
from collections import Counter
from urllib.parse import urlparse

from plone import api
from plone.restapi.blocks import visit_blocks

from eea.climateadapt.scripts import get_plone_site

RESOLVEUID_RE = re.compile(r"resolveuid/([a-fA-F0-9\-]+)")

INTERNAL_HOSTS = (
    "climate-adapt.eea.europa.eu",
    "demo-climate-adapt.02pre.eea.europa.eu",
    "localhost",
    "cca.localhost",
    "10.50.5.50",
)


def walk_block(block, prefix=""):
    """Yield (fieldpath, value) for every string inside one block dict.

    Descends into slate nodes and arbitrary nested dicts/lists, but not into
    nested block containers (those are handled by visit_blocks).
    """
    for key, value in block.items():
        if key in ("blocks", "blocks_layout"):
            continue
        if key == "data" and isinstance(value, dict) and "blocks" in value:
            continue
        if isinstance(value, str):
            yield f"{prefix}{key}", value
        elif isinstance(value, dict):
            yield from walk_block(value, f"{prefix}{key}.")
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield from walk_block(item, f"{prefix}{key}[].")


def classify(value):
    """Classify a string found in a block. Returns (kind, key, raw)."""
    if not value or not isinstance(value, str):
        return None
    if "resolveuid" in value:
        m = RESOLVEUID_RE.search(value)
        if m:
            return ("resolveuid", m.group(1), value)
        return ("resolveuid-malformed", None, value)
    parsed = urlparse(value)
    if parsed.netloc in INTERNAL_HOSTS:
        return ("absolute-internal", parsed.path, value)
    if parsed.netloc:
        return ("external-host", parsed.netloc, value)
    if value.startswith("/"):
        return ("root-relative", value, value)
    return None


def main():
    parser = argparse.ArgumentParser(prog="scan_block_links")
    parser.add_argument("--portal", dest="portal_id", required=True)
    parser.add_argument("--zope-conf", dest="zope_conf", required=True)
    parser.add_argument("--path", dest="path", default="/en")
    parser.add_argument("--out", dest="out", default="")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--no-uid-check", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    site = get_plone_site(args.zope_conf, args.portal_id)
    portal_path = "/".join(site.getPhysicalPath())
    query_path = f"{portal_path}/{args.path.strip('/')}".rstrip("/")

    brains = api.content.find(context=site, path={"query": query_path})
    print(f"Found {len(brains)} objects under {query_path}", flush=True)

    shape = Counter()
    kinds = Counter()
    records = []
    uids = set()
    scanned = 0

    for brain in brains:
        try:
            obj = brain.getObject()
            blocks = getattr(obj, "blocks", None)
            if not isinstance(blocks, dict) or not blocks:
                continue
            scanned += 1
            opath = "/".join(obj.getPhysicalPath())
            found = 0
            for block in visit_blocks(obj, blocks):
                if not isinstance(block, dict):
                    continue
                btype = block.get("@type")
                for field, value in walk_block(block):
                    cls = classify(value)
                    if cls is None:
                        continue
                    kind, key, raw = cls
                    shape[(btype, field, kind)] += 1
                    kinds[kind] += 1
                    found += 1
                    record = {
                        "object": opath,
                        "block_type": btype,
                        "field": field,
                        "kind": kind,
                        "value": raw,
                    }
                    if kind == "resolveuid":
                        uids.add(key)
                    records.append(record)
            if found and args.verbose:
                print(f"{opath}: {found} links", flush=True)
            if scanned % 250 == 0:
                print(f"... scanned {scanned}", flush=True)
            if args.limit and scanned >= args.limit:
                break
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR on {brain.getPath()}: {exc}", flush=True)

    print(f"\nObjects with blocks: {scanned}")
    print("\n--- link kinds ---")
    for kind, count in kinds.most_common():
        print(f"{kind:24} {count}")
    print("\n--- top (block_type, field, kind) ---")
    for (btype, field, kind), count in shape.most_common(60):
        print(f"{str(btype):24} {field:34} {kind:20} {count}")

    missing = set()
    if uids and not args.no_uid_check:
        catalog = api.portal.get_tool("portal_catalog")
        uid_list = sorted(uids)
        for i in range(0, len(uid_list), 200):
            chunk = uid_list[i : i + 200]
            found_uids = {b.UID for b in catalog(UID=chunk)}
            missing.update(set(chunk) - found_uids)
        print(f"\nUnique referenced UIDs: {len(uid_list)}")
        print(f"UIDs NOT in catalog: {len(missing)}")
        by_user = {}
        for rec in records:
            m = RESOLVEUID_RE.search(rec["value"])
            if m and m.group(1) in missing:
                by_user.setdefault(m.group(1), []).append(
                    (rec["object"], rec["block_type"], rec["field"])
                )
        for uid, users in list(by_user.items())[:50]:
            print(uid, "<-", users[:2])

    if args.out:
        with open(args.out, "w") as fp:
            json.dump(records, fp, indent=1)
        print(f"\nWrote {len(records)} records to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
