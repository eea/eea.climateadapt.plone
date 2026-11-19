"""EXPLORATION ONLY: verify APIs needed by the fixer."""

from plone import api
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.redirector.storage import IRedirectionStorage
from zope.component import getUtility

from eea.climateadapt.scripts import get_plone_site

site = get_plone_site("/app/etc/relstorage.conf", "cca")
catalog = api.portal.get_tool("portal_catalog")

print("ILanguageRootFolder import OK:", ILanguageRootFolder)

q = catalog(path={"query": "/cca/en/mission"})
print("path query /cca/en/mission ->", len(q))
q2 = catalog(path={"query": "/cca/en/mission", "depth": -1})
print("with depth -1 ->", len(q2))
q3 = catalog(path="/cca/en/mission")
print("string path ->", len(q3))
print("sample:", [b.getPath() for b in q3[:3]])

print(
    "object_provides IBlocks ->",
    len(
        catalog(
            object_provides="plone.restapi.behaviors.IBlocks",
            path={"query": "/cca/en/mission"},
        )
    ),
)

storage = getUtility(IRedirectionStorage)
print("redirector entries:", len(storage))
print("has_path /cca/en/mission:", storage.has_path("/cca/en/mission"))
print("get /cca/en/mission:", storage.get("/cca/en/mission"))
print("iter sample:", list(storage)[:5])
print("redirects('/cca/en/mission'):", list(storage.redirects("/cca/en/mission"))[:5])

# language root folders
for k, v in site.items():
    if ILanguageRootFolder.providedBy(v):
        print("LRF:", k)
