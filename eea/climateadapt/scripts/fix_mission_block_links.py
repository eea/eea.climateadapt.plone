"""Repair internal references inside Volto blocks after the mission
reorganisation (``/en/mission`` -> ``/en/eu-policy/eu-adaptation-policy/
eu-mission-on-adaptation`` + ``/en/mission-inactive``).

The reorganisation re-created part of the old mission tree with **new UIDs**,
so blocks that point at the old UIDs are dead, while blocks that point at old
*paths* still work only because ``plone.app.redirector`` aliases exist.

Strategy, per reference found in a block:

1. work out the **old** (pre-reorg) path of the target:
   * ``resolveuid/<uid>`` -> looked up in the dictionary exported by
     ``export_uid_paths`` from the pre-reorg database;
   * absolute-internal / root-relative values -> the path in the value itself.
2. map old path -> new path with ``plone.app.redirector``'s
   ``IRedirectionStorage`` (following alias chains, including aliases registered
   on an ancestor folder), with an ``id``-based fallback for the cases where the
   alias exists but the target folder was also renamed (e.g.
   ``images/step-1.3`` -> ``images/1.3``), and with ``--rename-rule`` for the
   folders that were renamed without any alias at all;
3. rewrite the value, keeping its original form (resolveuid stays resolveuid,
   absolute URL stays an absolute URL, path stays a path).

Dry-run by default: nothing is written unless ``--apply`` is given.

    docker compose exec backend /app/docker-entrypoint.sh \
        bin/fix_mission_block_links --portal cca --zope-conf etc/relstorage.conf \
        --uid-map /app/import/mission_uid_paths.json --csv /tmp/report.csv

    # then
    docker compose exec backend /app/docker-entrypoint.sh \
        bin/fix_mission_block_links --portal cca --zope-conf etc/relstorage.conf \
        --uid-map /app/import/mission_uid_paths.json --csv /tmp/report.csv --apply
"""

import argparse
import csv
import json
import logging
import re
import sys
import unicodedata
from urllib.parse import urlparse

import transaction
from Acquisition import aq_base
from plone import api
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.redirector.storage import IRedirectionStorage
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityContainer
from plone.restapi.deserializer.utils import path2uid
from zope.component import getUtility

from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.scripts._blocks import (
    ABSOLUTE_INTERNAL,
    EXTERNAL,
    RESOLVEUID,
    classify,
    iter_blocks,
    iter_strings,
    split_suffix,
)

logger = logging.getLogger("fixer")

INTERNAL_HOSTS = (
    "climate-adapt.eea.europa.eu",
    "demo-climate-adapt.02pre.eea.europa.eu",
)

DEFAULT_PATHS = (
    "/en/eu-policy/eu-adaptation-policy/eu-mission-on-adaptation",
    "/en/mission-inactive",
)

DEFAULT_RESTRICT = ("/en/mission",)

FIXED = "FIXED"
UNRESOLVED = "UNRESOLVED"
LEFT_CCA = "LEFT-CCA"
ALIVE = "ALIVE"
ALIVE_ALIAS = "ALIVE-VIA-ALIAS"
NOT_IN_MAP = "NOT-IN-MAP"
OUT_OF_SCOPE = "OUT-OF-SCOPE"
TEXT_OCCURRENCE = "TEXT-OCCURRENCE"

# slate fields that hold display text, not links
TEXT_FIELDS = ("text", "plaintext")


def normalise_name(value, dots=False):
    """Normalise a file name for matching: ``Asset 98@2x.png`` -> ``asset-98-2x.png``.

    Editors often put the original upload name in the block's ``alt`` while Plone
    normalised the object id (spaces/underscores to dashes, ``@`` to a dash,
    accents stripped, lower case). With ``dots`` the remaining dots are folded to
    dashes too, which is what Plone did to names like ``Asset 70@1.5x.png``
    (object id ``asset-70-1-5x.png``).
    """
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = value.lower().replace("@", "-")
    if dots:
        value = value.replace(".", "-")
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def name_keys(value):
    """Every normalisation form a name may be stored or typed under.

    The stem forms matter because Plone may or may not keep the extension; the
    dotted forms because Plone folded dots into dashes for names such as
    ``Asset 70@1.5x.png`` (object id ``asset-70-1-5x.png``).
    """
    stem = value.rsplit(".", 1)[0] if "." in value else value
    return {
        normalise_name(value),
        normalise_name(value, dots=True),
        normalise_name(stem),
        normalise_name(stem, dots=True),
    }


class Resolver(object):
    """Resolves old (pre-reorg) paths to objects of the current database."""

    def __init__(
        self, site, uid_paths, block_join, restrict, scan_roots, rename_rules=()
    ):
        self.site = site
        self.portal_path = "/".join(site.getPhysicalPath())
        self.catalog = api.portal.get_tool("portal_catalog")
        self.storage = getUtility(IRedirectionStorage)
        self.uid_paths = uid_paths
        self.block_join = block_join
        self.restrict = restrict
        self.scan_roots = scan_roots
        self.rename_rules = tuple(rename_rules)
        self._uid_cache = {}
        self._alias_cache = {}
        self._anc_cache = {}
        self._name_index = None

    # -- lookups ---------------------------------------------------------
    def uid_to_rel(self, uid):
        """Return the current portal-relative path for a UID, or None."""
        if uid not in self._uid_cache:
            brains = self.catalog(UID=uid)
            self._uid_cache[uid] = (
                brains[0].getPath()[len(self.portal_path) :] if brains else None
            )
        return self._uid_cache[uid]

    def traverse(self, rel):
        if not rel:
            return None
        physical = f"{self.portal_path}{rel}"
        try:
            obj = self.site.unrestrictedTraverse(physical, None)
        except Exception:  # noqa: BLE001
            obj = None
        if obj is None or not IDexterityContent.providedBy(obj):
            return None
        return obj

    def follow_alias(self, rel):
        """Follow the alias chain for a portal-relative path."""
        if rel in self._alias_cache:
            return self._alias_cache[rel]
        physical = f"{self.portal_path}{rel}"
        current = physical
        for _step in range(10):
            nxt = self.storage.get(current)
            if not nxt or nxt == current:
                break
            current = nxt
        result = (
            current[len(self.portal_path) :]
            if current.startswith(self.portal_path)
            else current
        )
        self._alias_cache[rel] = result
        return result

    def ancestor_alias(self, rel):
        """Nearest *ancestor* of ``rel`` that has an alias, with the path rebuilt.

        Aliases are registered per moved object, not for everything below it. A
        folder that was renamed without an alias (``images/step-1.3`` ->
        ``images/1.3``) or leaf content that was never aliased (images) still
        resolves if an ancestor was aliased:

            /en/mission/.../regional-adaptation-support-tool  ->  <new tree>
            /en/mission/.../regional-adaptation-support-tool/images/1.1/x.png
              => <new tree>/images/1.1/x.png

        Returns ``(new_rel, aliased_ancestor, rename_rule)``; ``new_rel`` is
        ``None`` when nothing resolves. ``rename_rule`` is the ``--rename-rule``
        that was needed, if any: some folders were renamed as well as moved
        (``images/step-1.3`` -> ``images/1.3``), so the rebuilt remainder has to
        be rewritten before it resolves.
        """
        if rel in self._anc_cache:
            return self._anc_cache[rel]
        segments = [s for s in rel.split("/") if s]
        result = (None, None, "")
        # start below the full path: the exact alias is handled by follow_alias
        for i in range(len(segments) - 1, 0, -1):
            ancestor = "/" + "/".join(segments[:i])
            target = self.storage.get(f"{self.portal_path}{ancestor}")
            if not target or target == f"{self.portal_path}{ancestor}":
                continue
            if target.startswith(self.portal_path):
                target = target[len(self.portal_path) :]
            candidate = f"{target}/{'/'.join(segments[i:])}"
            if self.traverse(candidate):
                result = (candidate, ancestor, "")
                break
            for old_seg, new_seg in self.rename_rules:
                if old_seg not in candidate:
                    continue
                moved = candidate.replace(old_seg, new_seg)
                if self.traverse(moved):
                    result = (moved, ancestor, f"{old_seg}->{new_seg}")
                    break
            if result[0]:
                break
        self._anc_cache[rel] = result
        return result

    def _by_id(self, rel):
        """Find an object whose parent moved but whose own folder was renamed."""
        segments = [s for s in rel.split("/") if s]
        if not segments:
            return None
        wanted_id = segments[-1]
        parent = "/" + "/".join(segments[:-1])
        parent_obj = self.traverse(parent)
        candidates = []
        if parent_obj is not None:
            # the catalog path index needs the physical path, not the
            # portal-relative one
            candidates = self.catalog(path=f"{self.portal_path}{parent}", id=wanted_id)
        if len(candidates) != 1:
            hits = []
            for root in self.scan_roots:
                root_obj = self.traverse(root)
                if root_obj is None:
                    continue
                hits.extend(
                    self.catalog(path=f"{self.portal_path}{root}", id=wanted_id)
                )
            uids = {brain.UID for brain in hits}
            if len(uids) == 1:
                candidates = hits[:1]
        if len(candidates) == 1:
            brain = candidates[0]
            return brain.getPath()[len(self.portal_path) :]
        return None

    def is_internal_url(self, url):
        """True for URLs that stay inside the Climate-ADAPT portal."""
        netloc = urlparse(url).netloc
        if netloc in INTERNAL_HOSTS:
            return True
        return netloc.endswith("eea.europa.eu") and not netloc.startswith(
            "mission-adaptation-portal"
        )

    def _left_cca(self, obj):
        """True when the target is a Redirection to a site outside the portal."""
        remote = getattr(obj, "remoteUrl", None)
        if not remote or not remote.startswith("http"):
            return False
        return not self.is_internal_url(remote)

    def old_to_new(self, old_rel):
        """Return ``(new_rel, note)``; ``new_rel`` is None when unresolvable."""
        aliased = self.follow_alias(old_rel)
        if aliased != old_rel:
            obj = self.traverse(aliased)
            if obj is not None:
                return (None, "left-cca") if self._left_cca(obj) else (aliased, "alias")
        obj = self.traverse(old_rel)
        if obj is not None:
            if self._left_cca(obj):
                return None, "left-cca"
            return old_rel, "unchanged"
        by_ancestor, ancestor, rule = self.ancestor_alias(old_rel)
        if by_ancestor:
            obj = self.traverse(by_ancestor)
            if obj is not None and self._left_cca(obj):
                return None, "left-cca"
            note = f"alias-ancestor({ancestor})"
            if rule:
                note += f" + rename({rule})"
            return by_ancestor, note
        by_id = self._by_id(aliased)
        if by_id:
            return by_id, "alias+id"
        by_id = self._by_id(old_rel)
        if by_id:
            return by_id, "id"
        return None, "unresolved"

    # -- reference handling ---------------------------------------------
    def old_path_for(self, kind, key, obj_rel, block_id, field):
        """Work out the pre-reorg path a reference used to point at."""
        if kind == RESOLVEUID:
            old = self.uid_paths.get(key)
            if old:
                return old, "uid-map"
            old = self.old_from_block_join(obj_rel, block_id, field)
            if old:
                return old, "block-join"
            return None, "uid-not-in-map"
        return key, "value"

    def old_from_block_join(self, obj_rel, block_id, field):
        """Fallback: the same block in the pre-reorg copy of this object."""
        if not self.block_join:
            return None
        physical = f"{self.portal_path}{obj_rel}"
        for old_physical in self.storage.redirects(physical):
            # redirects() answers with physical paths, the map is keyed
            # portal-relative
            old_obj_rel = (
                old_physical[len(self.portal_path) :]
                if old_physical.startswith(self.portal_path)
                else old_physical
            )
            entries = self.block_join.get(old_obj_rel)
            if not entries:
                continue
            for entry in entries:
                if entry["block_id"] == block_id and entry["field"] == field:
                    return entry["target"]
        return None

    def in_scope(self, old_rel):
        return any(old_rel.startswith(prefix) for prefix in self.restrict)

    # -- alt text fallback ----------------------------------------------
    def build_name_index(self):
        """Index every Image/File id under the scanned subtrees."""
        index = {}
        for root in self.scan_roots:
            root_obj = self.traverse(root)
            if root_obj is None:
                continue
            brains = self.catalog(
                portal_type=("Image", "File"),
                path=f"{self.portal_path}{root}",
            )
            for brain in brains:
                rel = brain.getPath()[len(self.portal_path) :]
                for key in name_keys(brain.getId):
                    if key:
                        index.setdefault(key, set()).add(rel)
        self._name_index = index
        return index

    def alt_match(self, alt, obj_rel):
        """Path of the image a dead reference meant, taken from the block's alt.

        Accepted only when exactly one object matches, so an ambiguous alt text
        is reported instead of guessed. The one exception is the common case of
        the same file existing both inside the page's own folder and in a shared
        images folder: a child of the referencing page wins, because that is
        where Volto stores an inline upload.
        """
        if not alt:
            return None
        if self._name_index is None:
            self.build_name_index()
        candidates = None
        for key in name_keys(alt):
            if key and key in self._name_index:
                candidates = self._name_index[key]
                break
        if not candidates:
            return None
        if len(candidates) > 1:
            parent = obj_rel.rstrip("/")
            own = {c for c in candidates if c.rsplit("/", 1)[0] == parent}
            if len(own) != 1:
                return None
            return next(iter(own))
        return next(iter(candidates))


def rewrite_value(kind, value, new_rel, target_obj, context_obj, suffix):
    """Build the replacement value, keeping the original form."""
    if kind == RESOLVEUID:
        return path2uid(context=context_obj, link=target_obj.absolute_url()) + suffix
    if kind == ABSOLUTE_INTERNAL:
        marker = "://"
        if marker in value:
            scheme, rest = value.split(marker, 1)
            host = rest.split("/", 1)[0]
            return f"{scheme}://{host}{new_rel}{suffix}"
        return new_rel + suffix
    # ROOT_RELATIVE
    return new_rel + suffix


def main():
    parser = argparse.ArgumentParser(prog="fix_mission_block_links")
    parser.add_argument("--portal", dest="portal_id", required=True, help="Portal ID")
    parser.add_argument(
        "--zope-conf", dest="zope_conf", required=True, help="Path to zope.conf"
    )
    parser.add_argument(
        "--uid-map",
        dest="uid_map",
        required=True,
        help="JSON {uid: old portal-relative path} from export_uid_paths",
    )
    parser.add_argument(
        "--block-join",
        dest="block_join",
        default="",
        help="Optional JSON block map from export_uid_paths (fallback lookup)",
    )
    parser.add_argument(
        "--path",
        dest="paths",
        action="append",
        default=[],
        metavar="PATH",
        help="Portal-relative subtree to scan; '*' = language code. Repeatable. "
        f"Default: {', '.join(DEFAULT_PATHS)}",
    )
    parser.add_argument(
        "--restrict",
        dest="restrict",
        action="append",
        default=[],
        metavar="PATH",
        help="Only rewrite references whose old path starts with this prefix. "
        f"Default: {', '.join(DEFAULT_RESTRICT)}",
    )
    parser.add_argument(
        "--normalize-aliasable",
        action="store_true",
        help="Also rewrite references that currently resolve only thanks to an "
        "alias. Off by default (they work, but they depend on the aliases).",
    )
    parser.add_argument(
        "--rewrite-text",
        action="store_true",
        help="Also rewrite URLs that appear inside slate display text "
        "(text/plaintext fields). Off by default.",
    )
    parser.add_argument(
        "--no-alt-match",
        action="store_true",
        help="Do not pair a dead reference with an image using the block's alt "
        "text (used only when the alt text matches exactly one image id).",
    )
    parser.add_argument(
        "--rename-rule",
        dest="rename_rules",
        action="append",
        default=[],
        metavar="OLD=NEW",
        help="Folder renamed together with the move, applied to the rebuilt "
        "candidate path. Repeatable, e.g. --rename-rule images/step-1.3=images/1.3",
    )
    parser.add_argument(
        "--traverse",
        action="store_true",
        help="Enumerate objects by walking the tree instead of using the catalog "
        "(slower, but immune to stale catalog entries)",
    )
    parser.add_argument("--apply", action="store_true", help="Write the changes")
    parser.add_argument("--limit", type=int, default=0, help="Stop after N objects")
    parser.add_argument(
        "--commit-every", type=int, default=50, help="Commit every N changed objects"
    )
    parser.add_argument(
        "--csv", dest="csv_file", default="mission_block_links_report.csv"
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    site = get_plone_site(args.zope_conf, args.portal_id)
    portal_path = "/".join(site.getPhysicalPath())

    request = getattr(site, "REQUEST", None)
    if request is not None:
        # never let a stray modified event enqueue translation jobs
        request.disable_object_modified_handler = True

    with open(args.uid_map) as fp:
        uid_paths = json.load(fp)
    block_join = {}
    if args.block_join:
        with open(args.block_join) as fp:
            block_join = json.load(fp)

    def expand(patterns):
        out = []
        for pattern in patterns:
            if "*" in pattern:
                for lang in [
                    child.getId()
                    for _id, child in site.items()
                    if ILanguageRootFolder.providedBy(child)
                ]:
                    out.append(pattern.replace("*", lang))
            else:
                out.append(pattern)
        return [p.strip("/") for p in out]

    scan_paths = expand(args.paths or list(DEFAULT_PATHS))
    restrict = [f"/{p}" for p in expand(args.restrict or list(DEFAULT_RESTRICT))]
    scan_roots = [f"/{p}" for p in scan_paths]

    rename_rules = []
    for rule in args.rename_rules:
        if "=" not in rule:
            parser.error(f"--rename-rule needs OLD=NEW, got {rule!r}")
        old_seg, new_seg = rule.split("=", 1)
        rename_rules.append((old_seg.strip("/"), new_seg.strip("/")))
    for old_seg, new_seg in rename_rules:
        logger.info("rename rule: %s -> %s", old_seg, new_seg)

    resolver = Resolver(site, uid_paths, block_join, restrict, scan_roots, rename_rules)

    catalog = api.portal.get_tool("portal_catalog")
    targets = []
    if args.traverse:
        for root_rel in scan_roots:
            root_obj = site.unrestrictedTraverse(f"{portal_path}{root_rel}", None)
            if root_obj is None:
                logger.warning("missing %s", root_rel)
                continue
            stack = [root_obj]
            seen = set()
            count = 0
            while stack:
                node = stack.pop()
                try:
                    path = "/".join(node.getPhysicalPath())
                    if path in seen:
                        continue
                    seen.add(path)
                    # NB: aq_base for the blocks check and IDexterityContainer for
                    # the descent - both ``blocks`` and ``items``/``objectValues``
                    # are otherwise acquired from the parent folder, which makes
                    # images look block-carrying and makes the walk loop forever.
                    if getattr(aq_base(node), "blocks", None):
                        targets.append(node)
                        count += 1
                    if IDexterityContainer.providedBy(node):
                        stack.extend(node.objectValues())
                except Exception as exc:  # noqa: BLE001
                    logger.warning("cannot walk %s: %s", node.getId(), exc)
            logger.info(
                "%s -> %s block objects (traversed, %s nodes visited)",
                root_rel,
                count,
                len(seen),
            )
    else:
        for path in scan_paths:
            found = catalog(
                path={"query": f"{portal_path}/{path}"},
                object_provides="plone.restapi.behaviors.IBlocks",
            )
            logger.info("%s -> %s block objects", path, len(found))
            targets.extend(found)

    rows = []
    counters = {}
    changed = 0
    scanned = 0

    def add_row(action, where, kind, old, new, note):
        """Record one decision. ``where`` is (obj_rel, container, bid, btype, field)."""
        counters[action] = counters.get(action, 0) + 1
        obj_rel, container, bid, btype, field = where
        rows.append(
            {
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

    for item in targets:
        if args.limit and scanned >= args.limit:
            break
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

        touched = False
        for bid, block, container in iter_blocks(obj):
            btype = block.get("@type")
            for holder, key, field, value in iter_strings(block):
                kind, ref = classify(value, INTERNAL_HOSTS)
                if kind == EXTERNAL or ref is None:
                    continue
                if field.split(".")[-1] in TEXT_FIELDS and not args.rewrite_text:
                    add_row(
                        TEXT_OCCURRENCE,
                        (obj_rel, container, bid, btype, field),
                        kind,
                        value[:300],
                        "",
                        "display text, not a link field (use --rewrite-text)",
                    )
                    continue

                current_rel = resolver.uid_to_rel(ref) if kind == RESOLVEUID else None
                if kind == RESOLVEUID:
                    if current_rel and resolver.traverse(current_rel):
                        counters[ALIVE] = counters.get(ALIVE, 0) + 1
                        continue
                else:
                    target = resolver.traverse(ref)
                    if target is not None:
                        aliased = resolver.follow_alias(ref)
                        action = ALIVE_ALIAS if aliased != ref else ALIVE
                        if action == ALIVE_ALIAS and not args.normalize_aliasable:
                            add_row(
                                action,
                                (obj_rel, container, bid, btype, field),
                                kind,
                                value,
                                "",
                                f"resolves via alias to {aliased}",
                            )
                            continue
                        if action == ALIVE:
                            counters[action] = counters.get(action, 0) + 1
                            continue

                old_rel, how = resolver.old_path_for(kind, ref, obj_rel, bid, field)
                new_rel = None
                note = ""
                if not old_rel:
                    # last resort: the block's alt text often carries the file
                    # name of the image that was picked
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
                            how if not alt else f"{how}; alt {alt!r} matched nothing",
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
                        action = LEFT_CCA if note == "left-cca" else UNRESOLVED
                        add_row(
                            action,
                            (obj_rel, container, bid, btype, field),
                            kind,
                            value,
                            "",
                            f"old={old_rel} ({how})",
                        )
                        continue

                target_obj = resolver.traverse(new_rel)
                if target_obj is None:
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
                new_value = rewrite_value(kind, value, new_rel, target_obj, obj, suffix)
                if new_value == value:
                    continue

                add_row(
                    FIXED,
                    (obj_rel, container, bid, btype, field),
                    kind,
                    value,
                    new_value,
                    f"{how} -> {note}",
                )
                if args.apply:
                    holder[key] = new_value
                    touched = True

        if touched and args.apply:
            obj.blocks = blocks
            obj._p_changed = True
            changed += 1
            if changed % args.commit_every == 0:
                transaction.commit()
                logger.info("committed %s objects", changed)
        if args.verbose:
            logger.info("scanned %s", obj_rel)

    if args.apply:
        transaction.commit()

    with open(args.csv_file, "w", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
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
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nScanned block objects: {scanned}")
    for action in (
        FIXED,
        ALIVE,
        ALIVE_ALIAS,
        UNRESOLVED,
        LEFT_CCA,
        NOT_IN_MAP,
        OUT_OF_SCOPE,
        TEXT_OCCURRENCE,
    ):
        print(f"  {action:18} {counters.get(action, 0)}")
    print(
        f"  objects written: {changed if args.apply else 0} (dry-run: {not args.apply})"
    )
    print(f"report: {args.csv_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
