2023-06-27 06:43:19 INFO ContentMigrate Migrating cca/pl/knowledge/european-climate-data-explorer/glossary-c3s
2023-06-27 06:43:19 WARNING eea.climateadapt GenericView tile converter not implemented: c3s_indicators_glossary_table

Traceback (most recent call last):
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/content.py", line 313, in migrate_content_to_volto
    migrate()
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/content.py", line 175, in __call__
    data = self.convert_tile_to_volto_blocklist(tileid)
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/content.py", line 100, in convert_tile_to_volto_blocklist
    data = converter(tile_dm, self.context, self.request)
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/tiles.py", line 253, in share_info_tile_to_block
    "href": link_url(),
  File "/plone/instance/src/eea.climateadapt/eea/climateadapt/migration/tiles.py", line 247, in link_url
    location, _t, factory = DEFAULT_LOCATIONS[type_]
KeyError: None


# TODO:

- On /en/knowledge/adaptation-information/climate-services/climate-services
  migrate links at top (first block) to table of contents block

slate crash in
- http://localhost:3000/en/observatory/policy-context/national-policy-analysis-2022

-
  http://localhost:8080/cca/en/about/outreach-and-dissemination/climate-adapt-events-and-webinars/compose

- http://localhost:3000/observatory-management-group-organisations
Uncaught Error: Objects are not valid as a React child (found: object with keys {i, o, v}). If you meant to render a collection of children, use an array instea
this is a collection.


Problems:

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

