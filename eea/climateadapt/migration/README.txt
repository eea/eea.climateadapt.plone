# TODO:

- On /en/knowledge/adaptation-information/climate-services/climate-services
  migrate links at top (first block) to table of contents block

- http://localhost:8080/cca/en/observatory/policy-context/european-policy-framework/working-group-on-health/eu-environment-health-process-WHO/edit
migrates with volto-slate problem

- http://localhost:3000/observatory-management-group-organisations
Uncaught Error: Objects are not valid as a React child (found: object with keys {i, o, v}). If you meant to render a collection of children, use an array instea


Problems:

<Cover at /cca/en/countries-regions/countries/switzerland>

DEBUG - 2023-05-19 08:39:21,350 - starlite - middleware - exception raised on http connection request to route /toblocks
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlite/middleware/exceptions/middleware.py", line 50, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlite/routes/http.py", line 79, in handle
    response = await self._get_response_for_request(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlite/routes/http.py", line 131, in _get_response_for_request
    response = await self._call_handler_function(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlite/routes/http.py", line 160, in _call_handler_function
    response_data, cleanup_group = await self._get_response_data(
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlite/routes/http.py", line 216, in _get_response_data
    data = route_handler.fn.value(**parsed_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main.py", line 39, in toblocks
    data = text_to_blocks(html)
           ^^^^^^^^^^^^^^^^^^^^
  File "/app/app/blocks.py", line 195, in text_to_blocks
    proc(soup)
  File "/app/app/blocks.py", line 92, in convert_tabs
    tab_id = li.a.attrs['href'].replace('#', '')
             ^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'attrs'



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

