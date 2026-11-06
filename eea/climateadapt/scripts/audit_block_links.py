"""Read-only inventory of broken internal references inside Volto blocks.

Companion to ``fix_mission_block_links``: same resolution rules, but it never
writes anything. Use it to answer "how many references are broken, where, and
which ones can be repaired automatically" - before a run, and to prove a run
worked afterwards.

The scan is done **one language at a time**. That matters: the ``alt``-text and
``id`` fallbacks build their candidate index from the scanned subtree, so with
several languages in scope at once every image id has one candidate per
language and every fallback silently turns into "ambiguous".

    docker compose exec -T backend /app/docker-entrypoint.sh \
        bin/audit_block_links --portal cca --zope-conf etc/relstorage.conf \
        --uid-map /app/import/mission_uid_paths.json \
        --path '/*/eu-policy/eu-adaptation-policy/eu-mission-on-adaptation' \
        --path '/*/mission-inactive' \
        --restrict '/*/mission' --restrict /en/mission \
        --csv /tmp/audit.csv

Every row of the report is a reference that does **not** currently resolve.
References that resolve are counted in the summary but not listed.

Actions:

* ``ALIVE``            - resolves, nothing to do (counted, not reported)
* ``ALIVE-VIA-ALIAS``  - resolves only thanks to an alias (reported)
* ``FIXED``            - would be rewritten by the fixer: target identified
* ``UNRESOLVED``       - old target known, but nothing lives at the new path
* ``NOT-IN-MAP``       - the old target cannot be worked out at all
* ``LEFT-CCA``         - target is a redirection to a site outside the portal
* ``OUT-OF-SCOPE``     - old target lies outside ``--restrict``
"""

import argparse
import csv
import json
import logging
import sys

from plone import api
from plone.app.multilingual.interfaces import ILanguageRootFolder

from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.scripts.fix_mission_block_links import ALIVE
from eea.climateadapt.scripts.fix_mission_block_links import ALIVE_ALIAS
from eea.climateadapt.scripts.fix_mission_block_links import EXTERNAL
from eea.climateadapt.scripts.fix_mission_block_links import FIXED
from eea.climateadapt.scripts.fix_mission_block_links import INTERNAL_HOSTS
from eea.climateadapt.scripts.fix_mission_block_links import LEFT_CCA
from eea.climateadapt.scripts.fix_mission_block_links import NOT_IN_MAP
from eea.climateadapt.scripts.fix_mission_block_links import OUT_OF_SCOPE
from eea.climateadapt.scripts.fix_mission_block_links import RESOLVEUID
from eea.climateadapt.scripts.fix_mission_block_links import TEXT_FIELDS
from eea.climateadapt.scripts.fix_mission_block_links import UNRESOLVED
from eea.climateadapt.scripts.fix_mission_block_links import Resolver
from eea.climateadapt.scripts.fix_mission_block_links import classify
from eea.climateadapt.scripts.fix_mission_block_links import iter_blocks
from eea.climateadapt.scripts.fix_mission_block_links import iter_strings
from eea.climateadapt.scripts.fix_mission_block_links import split_suffix

logger = logging.getLogger("audit_block_links")

DEFAULT_PATHS = (
    "/*/eu-policy/eu-adaptation-policy/eu-mission-on-adaptation",
    "/*/mission-inactive",
)

DEFAULT_RESTRICT = ("/*/mission", "/en/mission")

FIELDS = [
    "lang",
    "action",
    "object",
    "container",
    "block_id",
    "block_type",
    "field",
    "kind",
    "old",
    "new",
    "note",
]


def main():
    parser = argparse.ArgumentParser(prog="audit_block_links")
    parser.add_argument("--portal", dest="portal_id", required=True, help="Portal ID")
    parser.add_argument(
        "--zope-conf", dest="zope_conf", required=True, help="Path to zope.conf"
    )
    parser.add_argument(
        "--uid-map",
        dest="uid_map",
        required=True,
        help="JSON {uid: old portal-relative path}, see export_uid_paths",
    )
    parser.add_argument(
        "--block-join",
        dest="block_join",
        default="",
        help="Optional JSON block map (fallback lookup)",
    )
    parser.add_argument(
        "--path",
        dest="paths",
        action="append",
        default=[],
        metavar="PATH",
        help="Portal-relative subtree; '*' = language code. Repeatable. "
        f"Default: {', '.join(DEFAULT_PATHS)}",
    )
    parser.add_argument(
        "--restrict",
        dest="restrict",
        action="append",
        default=[],
        metavar="PATH",
        help="Only references whose old path starts with this prefix count as "
        f"in scope. Default: {', '.join(DEFAULT_RESTRICT)}",
    )
    parser.add_argument(
        "--rename-rule",
        dest="rename_rules",
        action="append",
        default=[],
        metavar="OLD=NEW",
        help="Folder renamed together with the move. Repeatable.",
    )
    parser.add_argument(
        "--no-alt-match",
        action="store_true",
        help="Do not use the block's alt text to identify a dead image",
    )
    parser.add_argument("--csv", dest="csv_file", default="block_links_audit.csv")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    site = get_plone_site(args.zope_conf, args.portal_id)
    portal_path = "/".join(site.getPhysicalPath())

    with open(args.uid_map) as fp:
        uid_paths = json.load(fp)
    block_join = {}
    if args.block_join:
        with open(args.block_join) as fp:
            block_join = json.load(fp)

    rename_rules = []
    for rule in args.rename_rules:
        if "=" not in rule:
            parser.error(f"--rename-rule needs OLD=NEW, got {rule!r}")
        old_seg, new_seg = rule.split("=", 1)
        rename_rules.append((old_seg.strip("/"), new_seg.strip("/")))

    languages = sorted(
        child.getId()
        for _id, child in site.items()
        if ILanguageRootFolder.providedBy(child)
    )

    path_patterns = args.paths or list(DEFAULT_PATHS)
    restrict_patterns = args.restrict or list(DEFAULT_RESTRICT)
    # group the scan subtrees by language, so each pass stays language-scoped
    per_lang = {}
    for pattern in path_patterns:
        for expanded in (
            [pattern.replace("*", lang) for lang in languages]
            if "*" in pattern
            else [pattern]
        ):
            lang = expanded.strip("/").split("/")[0]
            per_lang.setdefault(lang, []).append(f"/{expanded.strip('/')}")
    # a fixed prefix such as /en/mission applies to every language, because the
    # translated trees reference the English content as well
    fixed_restrict = [f"/{p.strip('/')}" for p in restrict_patterns if "*" not in p]

    catalog = api.portal.get_tool("portal_catalog")
    # one resolver for all languages: the UID/alias caches are language
    # independent, only the candidate index has to be rebuilt per language
    resolver = Resolver(site, uid_paths, block_join, [], [], rename_rules)

    with open(args.csv_file, "w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDS)
        writer.writeheader()

        totals = {}
        grand = {}
        for lang in sorted(per_lang):
            scan_roots = per_lang[lang]
            resolver.scan_roots = scan_roots
            resolver.restrict = sorted(
                set(fixed_restrict)
                | {
                    f"/{p.replace('*', lang).strip('/')}"
                    for p in restrict_patterns
                    if "*" in p
                }
            )
            resolver.reset_candidate_index()

            targets = []
            for root in scan_roots:
                found = catalog(
                    path={"query": f"{portal_path}{root}"},
                    object_provides="plone.restapi.behaviors.IBlocks",
                )
                logger.info("%s -> %s block objects", root, len(found))
                targets.extend(found)

            rows = []

            def add_row(action, where, kind, old, new, note):
                totals[action] = totals.get(action, 0) + 1
                obj_rel, container, bid, btype, field = where
                rows.append(
                    {
                        "lang": lang,
                        "action": action,
                        "object": obj_rel,
                        "container": container,
                        "block_id": bid,
                        "block_type": btype,
                        "field": field,
                        "kind": kind,
                        "old": old,
                        "new": new,
                        "note": note,
                    }
                )

            scanned = 0
            for item in targets:
                try:
                    obj = item.getObject() if hasattr(item, "getObject") else item
                except Exception as exc:  # noqa: BLE001
                    logger.error("cannot get %s: %s", getattr(item, "id", item), exc)
                    continue
                scanned += 1
                obj_rel = "/".join(obj.getPhysicalPath())[len(portal_path) :]
                blocks = obj.blocks
                if not isinstance(blocks, dict) or not blocks:
                    continue

                for bid, block, container in iter_blocks(obj):
                    btype = block.get("@type")
                    for holder, key, field, value in iter_strings(block):
                        kind, ref = classify(value, INTERNAL_HOSTS)
                        if kind == EXTERNAL or ref is None:
                            continue
                        if field.split(".")[-1] in TEXT_FIELDS:
                            continue

                        current_rel = (
                            resolver.uid_to_rel(ref) if kind == RESOLVEUID else None
                        )
                        if kind == RESOLVEUID:
                            if current_rel and resolver.traverse(current_rel):
                                totals[ALIVE] = totals.get(ALIVE, 0) + 1
                                continue
                        else:
                            target = resolver.traverse(ref)
                            if target is not None:
                                aliased = resolver.follow_alias(ref)
                                if aliased != ref:
                                    add_row(
                                        ALIVE_ALIAS,
                                        (obj_rel, container, bid, btype, field),
                                        kind,
                                        value,
                                        "",
                                        f"resolves via alias to {aliased}",
                                    )
                                else:
                                    totals[ALIVE] = totals.get(ALIVE, 0) + 1
                                continue

                        old_rel, how = resolver.old_path_for(
                            kind, ref, obj_rel, bid, field
                        )
                        new_rel = None
                        note = ""
                        if not old_rel:
                            alt = (holder.get("alt") or block.get("alt") or "").strip()
                            if kind == RESOLVEUID and alt and not args.no_alt_match:
                                new_rel = resolver.alt_match(alt, obj_rel)
                                if new_rel:
                                    how = "alt-match"
                                    note = f"alt={alt!r}"
                            if not new_rel:
                                add_row(
                                    NOT_IN_MAP,
                                    (obj_rel, container, bid, btype, field),
                                    kind,
                                    value,
                                    "",
                                    how
                                    if not alt
                                    else f"{how}; alt {alt!r} matched nothing",
                                )
                                continue
                        elif not resolver.in_scope(old_rel):
                            add_row(
                                OUT_OF_SCOPE,
                                (obj_rel, container, bid, btype, field),
                                kind,
                                value,
                                "",
                                f"old target {old_rel} outside --restrict",
                            )
                            continue
                        else:
                            new_rel, note = resolver.old_to_new(old_rel)
                            if new_rel is None:
                                add_row(
                                    LEFT_CCA if note == "left-cca" else UNRESOLVED,
                                    (obj_rel, container, bid, btype, field),
                                    kind,
                                    value,
                                    "",
                                    f"old={old_rel} ({how})",
                                )
                                continue

                        if resolver.traverse(new_rel) is None:
                            add_row(
                                UNRESOLVED,
                                (obj_rel, container, bid, btype, field),
                                kind,
                                value,
                                new_rel,
                                f"mapped but target missing ({old_rel or new_rel})",
                            )
                            continue

                        suffix = split_suffix(
                            value,
                            uid=ref if kind == RESOLVEUID else None,
                            path=ref if kind != RESOLVEUID else None,
                        )
                        add_row(
                            FIXED,
                            (obj_rel, container, bid, btype, field),
                            kind,
                            value,
                            new_rel + suffix,
                            f"{how} -> {note}",
                        )

            writer.writerows(rows)
            fp.flush()  # a long run stays usable even if it is interrupted
            for action, count in totals.items():
                grand[action] = grand.get(action, 0) + count
            print(
                f"{lang}: scanned={scanned} "
                + " ".join(f"{k}={v}" for k, v in sorted(totals.items())),
                flush=True,
            )
            totals = {}

    print("\nTotal per action:")
    for action in (
        FIXED,
        ALIVE,
        ALIVE_ALIAS,
        UNRESOLVED,
        LEFT_CCA,
        NOT_IN_MAP,
        OUT_OF_SCOPE,
    ):
        print(f"  {action:18} {grand.get(action, 0)}")
    print(f"report: {args.csv_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
