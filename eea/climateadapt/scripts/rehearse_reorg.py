"""EXPLORATION ONLY: rehearse the mission reorganisation on a development
database so that ``fix_mission_block_links`` can be exercised end to end.

    setup    build /en/sandbox/<id>-src (page + image), dump its uid map,
             copy the subtree (new UIDs), delete the original and register the
             aliases that production has
    verify   show the block values of the copied page and whether they resolve
    cleanup  delete the sandbox subtree and the aliases

Run with TRANSLATE_ON_CHANGE unset so content rules do not queue translations:

    docker compose exec -T -e TRANSLATE_ON_CHANGE= backend /app/docker-entrypoint.sh \
        /app/bin/python3 -m eea.climateadapt.scripts.rehearse_reorg setup
"""

import json
import logging
import sys
import time

import transaction
from plone import api
from plone.app.redirector.storage import IRedirectionStorage
from plone.dexterity.interfaces import IDexterityContainer
from plone.uuid.interfaces import IUUID
from zope.component import getUtility

from eea.climateadapt.scripts import get_plone_site

logger = logging.getLogger("rehearse")

DONOR = (
    "/en/mission/knowledge-and-data/regional-adaptation-support-tool/"
    "images/1.1/map-mission.png"
)
MANIFEST = "/tmp/rehearse_manifest.json"
UID_MAP = "/tmp/rehearse_uid_map.json"


def portal_rel(site, path):
    return path[len("/".join(site.getPhysicalPath())) :]


def setup(site):
    storage = getUtility(IRedirectionStorage)
    portal_path = "/".join(site.getPhysicalPath())

    sandbox = site.restrictedTraverse("en/sandbox", None)
    if sandbox is None:
        sandbox = api.content.create(
            container=site["en"], type="Folder", id="sandbox", title="Sandbox"
        )

    stamp = time.strftime("%Y%m%d%H%M%S")
    src_id = f"rehearse-{stamp}-src"
    dst_id = f"{src_id}-copy"

    base = api.content.create(
        container=sandbox, type="Folder", id=src_id, title="Rehearsal source"
    )
    images = api.content.create(container=base, type="Folder", id="images")
    donor = site.restrictedTraverse(DONOR.strip("/"))
    pic = api.content.copy(source=donor, target=images)
    transaction.commit()

    pic_uid = IUUID(pic)
    pic_rel = portal_rel(site, "/".join(pic.getPhysicalPath()))

    page = api.content.create(container=base, type="Folder", id="page", title="Page")
    page.blocks = {
        "b1": {"@type": "image", "url": f"../../resolveuid/{pic_uid}"},
        "b2": {
            "@type": "item",
            "image": f"https://climate-adapt.eea.europa.eu{pic_rel}",
        },
        "b3": {
            "@type": "callToActionBlock",
            "href": f"../../resolveuid/{pic_uid}/@@images/image/big",
        },
    }
    page.blocks_layout = {"items": ["b1", "b2", "b3"]}
    page._p_changed = True
    transaction.commit()
    logger.info("built %s (image uid %s)", "/".join(base.getPhysicalPath()), pic_uid)

    # dump the uid map for this subtree, as export_uid_paths would do.
    # NB: walked physically - this dev database has catalog entries missing for
    # freshly created content.
    uid_map = {}
    stack = [base]
    while stack:
        node = stack.pop()
        uid = IUUID(node, None)
        if uid:
            uid_map[uid] = portal_rel(site, "/".join(node.getPhysicalPath()))
        if IDexterityContainer.providedBy(node):
            stack.extend(node.objectValues())
    with open(UID_MAP, "w") as fp:
        json.dump(uid_map, fp, indent=1)
    logger.info("wrote %s entries to %s", len(uid_map), UID_MAP)

    # the reorganisation: copy the subtree (new UIDs), then delete the original
    dst = api.content.copy(source=base, target=sandbox, id=dst_id)
    # the copy is not always indexed when the translation subscribers blow up,
    # and the fixer works from the catalog
    stack = [dst]
    while stack:
        node = stack.pop()
        try:
            node.reindexObject()
        except Exception as exc:  # noqa: BLE001
            logger.warning("reindex failed for %s: %s", node.getId(), exc)
        if hasattr(node, "objectValues"):
            stack.extend(node.objectValues())
    transaction.commit()
    api.content.delete(base)
    transaction.commit()
    logger.info(
        "copied to %s and deleted the original", "/".join(dst.getPhysicalPath())
    )

    # production has aliases for the moved paths
    aliases = [
        (
            f"{portal_path}/en/sandbox/{src_id}/images/{pic.getId()}",
            f"{portal_path}/en/sandbox/{dst_id}/images/{pic.getId()}",
        ),
        (
            f"{portal_path}/en/sandbox/{src_id}/page",
            f"{portal_path}/en/sandbox/{dst_id}/page",
        ),
    ]
    for old, new in aliases:
        storage.add(old, new)
    transaction.commit()
    for old, new in aliases:
        logger.info("alias %s -> %s", old, new)

    manifest = {
        "src_id": src_id,
        "dst_id": dst_id,
        "pic_id": pic.getId(),
        "pic_uid_before": pic_uid,
        "aliases": aliases,
    }
    with open(MANIFEST, "w") as fp:
        json.dump(manifest, fp, indent=1)
    logger.info("manifest written to %s", MANIFEST)
    print(json.dumps(manifest, indent=1))
    return 0


def verify(site):
    with open(MANIFEST) as fp:
        manifest = json.load(fp)
    # the dev database does not index freshly created content, so resolve UIDs
    # by walking the sandbox subtree instead of using the catalog
    uids = {}
    root = site.restrictedTraverse(f"en/sandbox/{manifest['dst_id']}")
    stack = [root]
    while stack:
        node = stack.pop()
        uid = IUUID(node, None)
        if uid:
            uids[uid] = "/".join(node.getPhysicalPath())
        if IDexterityContainer.providedBy(node):
            stack.extend(node.objectValues())

    page = site.restrictedTraverse(f"en/sandbox/{manifest['dst_id']}/page")
    print(f"page blocks of en/sandbox/{manifest['dst_id']}/page")
    for bid, block in page.blocks.items():
        if bid == "blocks_layout":
            continue
        for key in ("url", "image", "href"):
            if key not in block:
                continue
            value = block[key]
            if "resolveuid" in value:
                uid = value.split("resolveuid/")[1].split("/")[0]
                alive = "ALIVE" if uid in uids else "DEAD"
            else:
                path = value.split("climate-adapt.eea.europa.eu")[-1]
                alive = (
                    "ALIVE"
                    if site.unrestrictedTraverse(path.split("/@@")[0].lstrip("/"), None)
                    else "DEAD"
                )
            print(f"  {bid} {block['@type']:18} {key:6} {alive:5} {value}")
    return 0


def cleanup(site):
    storage = getUtility(IRedirectionStorage)
    with open(MANIFEST) as fp:
        manifest = json.load(fp)
    node = site.restrictedTraverse(f"en/sandbox/{manifest['dst_id']}", None)
    if node is not None:
        api.content.delete(node)
    for old, _new in manifest["aliases"]:
        if storage.has_path(old):
            storage.remove(old)
    transaction.commit()
    logger.info("cleaned up %s", manifest["dst_id"])
    return 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "setup"
    site = get_plone_site("/app/etc/relstorage.conf", "cca")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if mode == "setup":
        return setup(site)
    if mode == "verify":
        return verify(site)
    if mode == "cleanup":
        return cleanup(site)
    print("usage: rehearse_reorg.py setup|verify|cleanup")
    return 1


if __name__ == "__main__":
    sys.exit(main())
