# TODO:

- On /en/knowledge/adaptation-information/climate-services/climate-services
  migrate links at top (first block) to table of contents block



Problems:


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


Example of cover:

[{u'children': [{u'children': [{u'id': u'1ab374eb8fb84e7ca45d45c6ed478889',
                                u'tile-type': u'eea.climateadapt.richtext_with_title',
                                u'type': u'tile'}],
                 u'column-size': 9,
                 u'css-class': u'content-column',
                 u'roles': [u'Manager'],
                 u'type': u'group'},
                {u'children': [{u'id': u'8df509b8122b48eaac79b3f2a4cfba83',
                                u'tile-type': u'eea.climateadapt.transregionselect',
                                u'type': u'tile'},
                               {u'id': u'f9c70eef-6442-4f00-b680-6012397531b0',
                                u'tile-type': u'eea.climateadapt.search_acecontent',
                                u'type': u'tile'}],
                 u'column-size': 3,
                 u'css-class': u'content-sidebar',
                 u'roles': [u'Manager'],
                 u'type': u'group'}],
  u'type': u'row'}]

[{u'children': [{u'children': [{u'id': u'd2ff69d4-9a08-489a-9f10-a5e2340beb68',
                                u'tile-type': u'eea.climateadapt.richtext_with_title',
                                u'type': u'tile'}],
                 u'column-size': 8,
                 u'id': u'group1',
                 u'roles': [u'Manager'],
                 u'type': u'group'},
                {u'children': [{u'id': u'fb3101ae-c16f-4ee6-8e43-b5c6d81b7a4a',
                                u'tile-type': u'eea.climateadapt.search_acecontent',
                                u'type': u'tile'},
                               {u'id': u'd43dcc10-4529-4ed4-afd6-1888a241671a',
                                u'tile-type': u'collective.cover.richtext',
                                u'type': u'tile'}],
                 u'column-size': 4,
                 u'roles': [u'Manager'],
                 u'type': u'group'}],
  u'type': u'row'},
 {u'children': [{u'children': [{u'id': u'df0fcc4c-94a3-4b90-88c7-821158e2ac9c',
                                u'tile-type': u'collective.cover.richtext',
                                u'type': u'tile'}],
                 u'column-size': 12,
                 u'roles': [u'Manager'],
                 u'type': u'group'}],
  u'type': u'row'}]

{
  full: {
    mobile: 12,
    tablet: 12,
    computer: 12,
  },
  halfWidth: {
    mobile: 12,
    tablet: 6,
    computer: 6,
  },
  twoThirds: {
    mobile: 12,
    tablet: 8,
    computer: 8,
  },
  oneThird: {
    mobile: 12,
    tablet: 4,
    computer: 4,
  },
  halfWidthBig: {
    mobile: 12,
    tablet: 8,
    computer: 6,
  },
  oneThirdSmall: {
    mobile: 12,
    tablet: 2,
    computer: 3,
  },
  oneQuarter: {
    mobile: 12,
    tablet: 6,
    computer: 3,
  },
  oneFifth: {
    mobile: 12,
    tablet: 2,
    computer: 3,
  },
  fourFifths: {
    mobile: 12,
    tablet: 10,
    computer: 9,
  },
  twoFifths: {
    mobile: 12,
    tablet: 10,
    computer: 5,
  },
  threeFifths: {
    mobile: 12,
    tablet: 10,
    computer: 7,
  },
};

