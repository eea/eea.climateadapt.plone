"""EXPLORATION ONLY: check the resolveuid rewrite helper end to end."""

from eea.climateadapt.scripts import get_plone_site
from eea.climateadapt.scripts._blocks import RESOLVEUID, split_suffix
from eea.climateadapt.scripts.fix_mission_block_links import rewrite_value

site = get_plone_site("/app/etc/relstorage.conf", "cca")

ctx = site.restrictedTraverse(
    "en/mission/knowledge-and-data/regional-adaptation-support-tool/"
    "step-1-preparing-the-ground-for-adaptation/step-1-1"
)
tgt = site.restrictedTraverse(
    "en/mission/knowledge-and-data/regional-adaptation-support-tool/images/1.1/"
    "map-mission.png"
)

cases = [
    "../../../../../../resolveuid/2795ae04741c400bb358e21bdc31e194",
    "../../../../../../resolveuid/2795ae04741c400bb358e21bdc31e194/@@images/image/big",
    "https://climate-adapt.eea.europa.eu/en/mission/x/images/1.1/map-mission.png",
    "/en/mission/x/images/1.1/map-mission.png/@@images/image/large",
]
new_rel = "/en/mission/knowledge-and-data/regional-adaptation-support-tool/images/1.1/map-mission.png"

for value in cases:
    if "resolveuid" in value:
        uid = value.split("resolveuid/")[1].split("/")[0]
        suffix = split_suffix(value, uid=uid)
        kind = RESOLVEUID
    else:
        uid = None
        from eea.climateadapt.scripts._blocks import (
            classify,
        )

        kind, ref = classify(value, ("climate-adapt.eea.europa.eu",))
        suffix = split_suffix(value, path=ref)
    print(f"OLD   {value}")
    print(f"  kind={kind} suffix={suffix!r}")
    print(f"NEW   {rewrite_value(kind, value, new_rel, tgt, ctx, suffix)}")
    print()
