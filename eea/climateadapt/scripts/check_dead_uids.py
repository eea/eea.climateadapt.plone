"""EXPLORATION ONLY: check whether UIDs referenced by production blocks can be
resolved against the (older) local snapshot, and how fresh the snapshot is.
"""

from plone import api

from eea.climateadapt.scripts import get_plone_site

site = get_plone_site("/app/etc/relstorage.conf", "cca")
catalog = api.portal.get_tool("portal_catalog")

newest = catalog(sort_on="modified", sort_order="reverse")[:5]
print("--- newest objects in local snapshot ---")
for b in newest:
    print("   ", b.modified, b.getPath())

uids = [u.strip() for u in open("/tmp/dead_uids.txt") if u.strip()]
print(f"\nchecking {len(uids)} production-dead UIDs against local snapshot")
found = 0
for uid in uids:
    res = catalog(UID=uid)
    if res:
        found += 1
        print(f"  FOUND {uid} -> {res[0].getPath()}")
    else:
        print(f"  ----- {uid}")
print(f"\nresolvable locally: {found}/{len(uids)}")
