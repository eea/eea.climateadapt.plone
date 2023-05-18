# TODO:

- On /en/knowledge/adaptation-information/climate-services/climate-services
  migrate links at top (first block) to table of contents block



Problems:

Traceback (most recent call last):
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/site.py", line 106, in _migrate_to_volto
    migrate()
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/cover.py", line 615, in __call__
    (cover, self.request), IMigrateToVolto)
  File "/plone/buildout-cache/eggs/zope.component-3.9.5-py2.7.egg/zope/component/_api.py", line 109, in getMultiAdapter
    raise ComponentLookupError(objects, interface, name)
ComponentLookupError: ((<Document at /cca/pl/observatory/policy-context/european-policy-framework/working-group-on-health/eu-environment-health-process-WHO>, <HTTPRequest, URL=http://localhost:8080/cca/@@volto_migrate_site>), <InterfaceClass eea.climateadapt.migration.interfaces.IMigrateToVolto>, u'')


2023-05-18 11:42:15 INFO eea.climateadapt Migrating cca/pl/observatory/policy-context/country-profiles/copy_of_country-profiles
2023-05-18 11:42:15 WARNING eea.climateadapt.cover You need to implement converter for block: <SchemaClass eea.climateadapt.tiles.genericview.IGenericViewTile>


2023-05-18 11:42:14 ERROR eea.climateadapt Error in migrating cca/pl/observatory/news-archive-observatory
Traceback (most recent call last):
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/site.py", line 106, in _migrate_to_volto
    migrate()
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/cover.py", line 613, in __call__
    if not getattr(cover.aq_inner.aq_self, 'blocks'):
  File "/plone/buildout-cache/eggs/plone.dexterity-2.3.1-py2.7.egg/plone/dexterity/content.py", line 340, in __getattr__
    raise AttributeError(name)
AttributeError: blocks


2023-05-18 11:42:14 ERROR eea.climateadapt Error in migrating cca/pl/observatory/evidence/projections-and-tools/exposure-vulnerable-groups
Traceback (most recent call last):
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/site.py", line 106, in _migrate_to_volto
    migrate()
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/cover.py", line 543, in __call__
    data = self.convert_tile_to_volto_blocklist(tileid)
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/cover.py", line 478, in convert_tile_to_volto_blocklist
    data = converter(tile_dm, self.context, self.request)
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/cover.py", line 123, in embed_tile_to_block                                                                                          if '<video' in embed:
TypeError: argument of type 'NoneType' is not iterable


2023-05-18 11:42:13 INFO eea.climateadapt Migrating cca/pl/knowledge/tools/copy_of_adaptation-support-tool/step-1-1/index_html
2023-05-18 11:42:13 WARNING eea.climateadapt.cover You need to implement converter for block: <SchemaClass eea.climateadapt.tiles.ast.IASTNavigationTile>
2023-05-18 11:42:13 WARNING eea.climateadapt.cover You need to implement converter for block: <SchemaClass eea.climateadapt.tiles.ast.IASTHeaderTile>
2023-05-18 11:42:13 WARNING eea.climateadapt.cover You need to implement converter for block: <SchemaClass eea.climateadapt.tiles.ast.IASTNavigationTile>
2023-05-18 11:42:13 WARNING eea.climateadapt.cover You need to implement converter for block: <SchemaClass eea.climateadapt.tiles.ast.IASTHeaderTile>

2023-05-18 11:42:14 INFO eea.climateadapt Migrating cca/pl/observatory/policy-context/country-profiles/austria
2023-05-18 11:42:14 WARNING eea.climateadapt.cover You need to implement converter for block: <SchemaClass eea.climateadapt.tiles.genericview.IGenericViewTile>
2023-05-18 11:42:14 WARNING eea.climateadapt.cover You need to implement converter for block: <SchemaClass eea.climateadapt.tiles.genericview.IGenericViewTile>
2023-05-18 11:42:14 INFO eea.climateadapt Migrating cca/pl/observatory/policy-context/country-profiles/belgium
