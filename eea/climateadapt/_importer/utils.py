""" Importing utils
"""

from eea.climateadapt._importer import sqlschema as sql
from plone.dexterity.utils import createContentInContainer
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import getUtility
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.site.hooks import getSite
import logging
import lxml.etree
import lxml.html
import random
import re
import urlparse


logger = logging.getLogger('eea.climateadapt.importer')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def printe(e):
    """ debug function to easily see an etree as pretty printed xml"""
    print lxml.etree.tostring(e, pretty_print=True)


def s2l(text, separator=';'):
    """Converts a string in form: u'EXTREMETEMP;FLOODING;' to a list"""
    return filter(None, text.split(separator))


def parse_settings(text):
    """Changes a string in form:
    # u'sitemap-changefreq=daily\nlayout-template-id=2_columns_iii\nsitemap-include=1\ncolumn-2=56_INSTANCE_9tMz,\ncolumn-1=56_INSTANCE_2cAx,56_INSTANCE_TN6e,\n'
    to a dictionary of settings
    """
    out = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        k, v = line.split('=', 1)
        v = filter(None, v.split(','))
        # if len(v) == 1:
        #     v = v[0]
        out[k] = v
    return out


def solve_dynamic_element(node):
    """ Used to extract content from xml etree. This is content stored by journal article
    """

    type_ = node.get('type')

    if type_ == 'image':
        # TODO: don't need to keep this as a list
        imageid = [str(x) for x in node.xpath("dynamic-content/@id")]
        return ('image', None, imageid)

    if type_ == 'text_area':
        return ('text',
                node.get('name'),
                [unicode(x) for x in node.xpath("dynamic-content/text()")]
                )

    if type_ == 'text_box':
        return (
            'dynamic',
            node.get('name'),
            [SOLVERS[child.tag](child) for child in node]
        )

    if type_ == 'text':
        return (
            'dynamic',
            node.get('name'),
            [SOLVERS[child.tag](child) for child in node]
        )

    if type_ in (None, 'list', 'boolean'):
        return (
            type_,
            node.get('name'),
            [SOLVERS[child.tag](child) for child in node]
        )

    raise ValueError("Dynamic element not handled, please write more code")


def solve_dynamic_content(node):
    return node.text
    # return ('text', None, node.text)


def solve_static_content(node):
    return node.text
    # return ('text', None, node.text)


SOLVERS = {
    'dynamic-element': solve_dynamic_element,
    'static-content': solve_static_content,
    'dynamic-content': solve_dynamic_content,
    # 'static-element': solve_static_element,
}


def strip_xml(xmlstr):
    if ("<xml" in xmlstr) or ("<?xml" in xmlstr):
        res = unicode(lxml.etree.fromstring(xmlstr.encode('utf-8')).xpath(
            "*/text()")[0])
    else:
        res = unicode(xmlstr)
    return res


def _clean(s):
    if s == "NULL_VALUE":
        return None
    return s


def _clean_portlet_settings(d):
    _conv = {
        'aceitemtype': 'search_type',
        'anyOfThese': 'special_tags',
        'countries': 'countries',
        'element': 'elements',
        'nrItemsPage': '10',
        'portletSetupTitle_en_GB': 'title',
        'sector': 'sector',
        'sortBy': 'sortBy'
    }
    res = {}
    for k, v in d.items():
        if k not in _conv:
            continue
        res[_conv[k]] = _clean(v)

    return res


def _get_portlet(session, portletid, layout):
    """ Get the portlet based on portletid and layout.plid

    layout.plid is the "portlet instance id" """
    try:
        portlet = session.query(sql.Portletpreference).filter_by(
            portletid=portletid, plid=layout.plid,
        ).one()
        return portlet
    except:
        return None


def _get_article_for_portlet(session, portlet):
    """ Parse portlet preferences to get the Journalarticle for the portlet """

    e = lxml.etree.fromstring(portlet.preferences)

    try:
        articleid = e.xpath(
            '//name[contains(text(), "articleId")]'
            '/following-sibling::value'
        )[0].text
    except IndexError:
        logger.debug("Couldn't find an article for portlet %s",
                        portlet.portletid)
        return

    article = session.query(sql.Journalarticle).filter_by(
        articleid=articleid, status=0).order_by(
            sql.Journalarticle.version.desc()
        ).first()

    return article


def extract_portlet_info(session, portletid, layout):
    """ Extract portlet information from the portlet with portletid

    The result can vary, based on what we find in a portlet.

    It can be:
        * a simple string with text
        * a list of ('type_of_info', info)
    """
    portlet = _get_portlet(session, portletid, layout)
    if portlet is None:
        logger.debug("Portlet id: %s could not be found for %s",
                       portletid, layout.friendlyurl)
        return

    if not portlet.preferences:
        logger.warning("Couldn't get preferences for portlet %s with plid %s",
                       portlet.portletid, portlet.plid)
        return

    # extract portlet settings, must be an application's settings
    e = lxml.etree.fromstring(portlet.preferences)
    prefs = {}
    for pref in e.xpath('//preference'):
        name = str(pref.find('name').text)
        value = pref.find('value')
        try:
            value = value.text
        except Exception:
            pass
        prefs[name] = unicode(value)

    portlet_title = None
    if prefs.get('portletSetupUseCustomTitle') == "true":
        for k, v in prefs.items():
            if k.startswith('portletSetupTitle'):
                portlet_title = unicode(v)

    article = _get_article_for_portlet(session, portlet)
    if article is not None:
        e = lxml.etree.fromstring(article.content.encode('utf-8'))

        # TODO: attach other needed metadata
        return {'title': article.title,
                'description': article.description,
                'content': [SOLVERS[child.tag](child) for child in e],
                'portlet_title': portlet_title,
                'portlet_type': 'journal_article_content'
                }

    logger.debug("Could not get an article from portlet %s for %s",
                    portletid, layout.friendlyurl)

    return prefs


def get_template_for_layout(layout):
    settings = parse_settings(layout.typesettings)

    if layout.type_ == u'link_to_layout':
        return "link to layout"

    template = settings['layout-template-id'][0]
    return template


def make_tile(cover, col):
    payload = col[0][1]
    if payload.get('portlet_type') == 'journal_article_content':
        _content = {
            'title': payload['portlet_title'] or "",
            'text': payload['content'][0]
        }
        return make_richtext_with_title_tile(cover, _content)

    if payload.get('paging') == u'1':
        # this is the search portlet on the right
        return make_aceitem_search_tile(cover, payload)
    else:
        return make_aceitem_relevant_content_tile(cover, payload)


def make_text_from_articlejournal(content):

    if not isinstance(content, list):
        raise ValueError

    if len(content) == 1:
        return content[0]

    if len(content) != 2:
        import pdb; pdb.set_trace()

    first_text = content[0][2][0]
    second_text = content[1][2][0]

    payload = {
        'first_text': first_text,
        'second_text': second_text
    }

    return render('templates/readmore_text.pt', payload)


def make_aceitem_search_tile(cover, info):
    # Available options
    # title
    # search_text
    # element_type
    # sector
    # special_tags
    # countries

    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.search_acecontent'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    info = _clean_portlet_settings(info)
    ITileDataManager(tile).set(info)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_transregion_dropdown_tile(cover):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.transregionselect'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    ITileDataManager(tile).set({'title': "Trans regional select"})

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_countries_dropdown_tile(cover):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.countryselect'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    ITileDataManager(tile).set({'title': "Country select"})

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_aceitem_relevant_content_tile(cover, payload):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.relevant_acecontent'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    info = _clean_portlet_settings(payload)
    ITileDataManager(tile).set(info)

    # TODO: relevant stuff here
    # info = _clean_portlet_settings(payload)
    # if filter(lambda x: x.startswith('user'), payload.keys()):
    #     return make_aceitem_relevant_content_tile(cover, payload)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_richtext_tile(cover, content):
    # creates a new tile and saves it in the annotation
    # returns a python objects usable in the layout description
    # content needs to be a dict with keys 'title' and 'text'

    site = getSite()

    id = getUtility(IUUIDGenerator)()
    typeName = 'collective.cover.richtext'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))

    content['text'] = fix_links(site, unicode(content['text']))
    content['title'] = unicode(content['title'])

    ITileDataManager(tile).set(content)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_richtext_with_title_tile(cover, content):
    # creates a new tile and saves it in the annotation
    # returns a python objects usable in the layout description
    # content needs to be a dict with keys 'title' and 'text'

    site = getSite()

    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.richtext_with_title'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))

    content['text'] = fix_links(site, unicode(content['text']))
    content['title'] = unicode(content['title'])

    ITileDataManager(tile).set(content)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_share_tile(cover, share_type):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.shareinfo'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))

    content = {}
    content['title'] = "Share your %s" % share_type
    content['shareinfo_type'] = share_type

    ITileDataManager(tile).set(content)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_iframe_embed_tile(cover, url):
    id = getUtility(IUUIDGenerator)()
    type_name = 'collective.cover.embed'
    tile = cover.restrictedTraverse('@@%s/%s' % (type_name, id))

    embed = "<iframe src='%s'></iframe>" % url

    ITileDataManager(tile).set({'title': 'embeded iframe', 'embed': embed})

    return {
        'tile-type': 'collective.cover.embed',
        'type': 'tile',
        'id': id
    }


# def make_ast_text_tile(cover, info):
#     id = getUtility(IUUIDGenerator)()
#     type_name = 'collective.cover.richtext'
#     tile = cover.restrictedTraverse('@@%s/%s' % (type_name, id))
#
#     payload = {
#         'title':None,
#         'subtitle': None,
#         'first_text': None,
#         'second_text': None,
#     }
#     country['Summary'] = render('templates/table.pt', table)
#
#     ITileDataManager(tile).set({'title': 'embeded iframe', 'embed': embed})
#
#     return {
#         'tile-type': 'collective.cover.embed',
#         'type': 'tile',
#         'id': id
#     }
#


def get_uuid_from_link(text):
    link = urlparse.urlparse(text)
    uuid = urlparse.parse_qs(link.query)['uuid'][0]
    return uuid


def fix_links(site, text):
    e = lxml.html.fromstring(text)
    imgs = e.xpath('//img')

    for img in imgs:
        src = img.get('src')
        uuid = get_uuid_from_link(src)
        image = get_image_by_uuid(site, uuid)
        url = image.absolute_url() + "/@@images/image"
        img.set('src', url)

    return lxml.html.tostring(e, pretty_print=True)


def get_image_by_imageid(site, imageid):
    repo = site['repository']
    reg = re.compile(str(imageid) + '.[jpg|png]')

    ids = [m.string for m in [reg.match(cid) for cid in repo.contentIds()] if m]

    if len(ids) != 1:
        raise ValueError("Image {} not found in repository".format(imageid))

    return repo[ids[0]]


def get_image_by_uuid(site, uuid):
    catalog = site['portal_catalog']
    return catalog.searchResults(imported_uuid=uuid)[0].getObject()


def make_image_tile(site, cover, info):
    id = getUtility(IUUIDGenerator)()
    type_name = 'collective.cover.banner'
    tile = cover.restrictedTraverse('@@%s/%s' % (type_name, id))

    imageid = info['id']
    image = get_image_by_imageid(site, imageid)
    tile.populate_with_object(image)
    return {
        'tile-type': type_name,
        'type': 'tile',
        'id': id
    }


def make_layout(*rows):
    return rows


def make_row(*cols):
    return {
        'type': 'row',
        'children': cols
    }


def make_column(*groups):
    return groups


# a layout contains rows
# a row can contain columns (in its children).
# a column will contain a group
# a group will have the tile

# sample cover layout. This is a JSON string!
# cover_layout = [
#     {"type": "row", "children":
#      [{"type": "group",
#        "children":
#        [
#            {"tile-type": "collective.cover.richtext", "type": "tile", "id": "be70f93bd1a4479f8a21ee595b001c06"}
#         ],
#        "roles": ["Manager"],
#        "column-size": 8},
#       {"type": "group",
#        "children":
#        [
#            {"tile-type": "collective.cover.embed", "type": "tile", "id": "face16b81f2d46bc959df9da24407d94"}
#        ],
#        "roles": ["Manager"],
#        "column-size": 8}]},
#     {"type": "row",
#      "children":
#         [
#             {"type": "group", "children":
#              [
#                  {"tile-type": "collective.cover.richtext", "type": "tile", "id": "a42d3c2a88c8430da52136e2a204cf25"}
#               ],
#              "roles": ["Manager"],
#              "column-size": 16}]}
# ]


# [{u'children': [{u'children': [None],
#                  'class': 'cell width-2 position-0',
#                  u'column-size': 2,
#                  u'roles': [u'Manager'],
#                  u'type': u'group'},
#                 {u'children': [{u'id': u'36759ad0c8114bb48467b858593b271f',
#                                 u'tile-type': u'collective.cover.richtext',
#                                 u'type': u'tile'}],
#                  'class': 'cell width-14 position-2',
#                  u'column-size': 14,
#                  u'roles': [u'Manager'],
#                  u'type': u'group'}],
#   'class': 'row',
#   u'type': u'row'}]
#


def make_group(size=16, *tiles):
    #{"type": "group", "children":
    #     [
    #         {"tile-type": "collective.cover.richtext", "type": "tile", "id": "a42d3c2a88c8430da52136e2a204cf25"}
    #      ],
    #     "roles": ["Manager"],
    #     "column-size": 16}]

    return {
        'type': 'group',
        'roles': ['Manager'],
        'column-size': size,
        'children': tiles
    }


def noop(*args, **kwargs):
    """ no-op function to help with development of importers.
    It avoids pyflakes errors about not used variables.
    """
    # pprint(args)
    # pprint(kwargs)
    return


def create_cover_at(site, location, id='index_html', **kw):
    parent = site

    for name in [x.strip() for x in location.split('/') if x.strip()]:
        if name not in parent.contentIds():
            parent = createContentInContainer(
                parent,
                'Folder',
                title=name,
            )
        else:
            parent = parent[name]

    cover = createContentInContainer(
        parent,
        'collective.cover.content',
        id=id,
        **kw
    )
    return cover


def log_call(wrapped):
    def wrapper(*args, **kwargs):
        logger.info("Calling %s", wrapped.func_name)
        return wrapped(*args, **kwargs)
    return wrapper


def render(path, options):
    tpl = PageTemplateFile(path, globals())
    ns = tpl.pt_getContext((), options)
    return tpl.pt_render(ns)


def render_accordion(payload):
    return render('templates/accordion.pt',
                          {'payload': payload,
                           'rand': lambda: unicode(random.randint(1, 10000))
                           }
                          )


def render_tabs(payload):
    return render('templates/tabs.pt',
                          {'payload': payload,
                           'rand': lambda: unicode(random.randint(1, 10000))
                           }
                          )

def pack_to_table(data):
    """ Convert a flat list of (k, v), (k, v) to a structured list
    """
    visited = []
    rows = []
    acc = []
    for k, v in data:
        if k not in visited:
            visited.append(k)
            acc.append(v)
        else:
            rows.append(acc)
            visited = [k]
            acc = [v]

    rows.append(acc)
    return {'rows': rows, 'cols': visited}


# Search portlet has this info:
#  u'column-5': [(u'filteraceitemportlet_WAR_FilterAceItemportlet_INSTANCE_nY73',
#                 {'aceitemtype': 'NULL_VALUE',
#                  'anyOfThese': 'urban',
#                  'countries': 'NULL_VALUE',
#                  'datainfo_type': '2',
#                  'element': 'NULL_VALUE',
#                  'freetextAny': '2',
#                  'fuzziness': None,
#                  'impact': 'NULL_VALUE',
#                  'nrItemsPage': '10',
#                  'paging': '1',
#                  'portletSetupTitle_en_GB': 'Search results',
#                  'portletSetupTitle_en_US': 'Search results',
#                  'portletSetupUseCustomTitle': 'true',
#                  'sector': 'NULL_VALUE',
#                  'sortBy': 'RATING'})],

# Relevant portlet info (aka listing of content) has this info:
#  u'column-4': [(u'simplefilterportlet_WAR_SimpleFilterportlet_INSTANCE_bZn6',
#                 {'aceitemtype': 'INFORMATIONSOURCE',
#                  'anyOfThese': 'countr-area-urban',
#                  'countries': 'NULL_VALUE',
#                  'datainfo_type': '2',
#                  'element': 'NULL_VALUE',
#                  'freeparameter': '0',
#                  'freetextAny': '2',
#                  'fuzziness': None,
#                  'impact': 'NULL_VALUE',
#                  'lfrWapInitialWindowState': 'NORMAL',
#                  'lfrWapTitle': None,
#                  'nrItemsPage': '7',
#                  'portletSetupCss': '',
#                  'portletSetupShowBorders': 'true',
#                  'portletSetupTitle_en_GB': 'Information Portals',
#                  'portletSetupTitle_en_US': 'Information Portals',
#                  'portletSetupUseCustomTitle': 'true',
#                  'sector': 'NULL_VALUE',
#                  'sortBy': 'RATING'})],


# sortBy is one of:
# set(['NAME', 'NULL_VALUE', 'RATING'])

# impact is always null value

# sector is one of:
# set([None,
#      'AGRICULTURE',
#      'BIODIVERSITY',
#      'COASTAL',
#      'DISASTERRISKREDUCTION',
#      'FINANCIAL',
#      'HEALTH',
#      'INFRASTRUCTURE',
#      'MARINE',
#      'NULL_VALUE',
#      'WATERMANAGEMENT'])

# freeparameter is one of:
# set([None, '0', '1', '2', '3'])

# element is one of :
# set([None, 'MEASUREACTION', 'NULL_VALUE', 'OBSERVATIONS', 'VULNERABILITY'])

# Possible values for anyOfThese:
# set([None,
#      'Ast1-2',
#      'Ast1-3',
#      'Baltic Sea Region',
#      'Baltic sea region policy',
#      'MAPLAYER',
#      'NATP',
#      'NATPCZECHREPUBLIC',
#      'NATPREG',
#      'NATPREG NORTHERN_IRELAND',
#      'NATPREG SCOTLAND',
#      'NATPREG WALES',
#      'SETOFMAPS',
#      'adapt-meas-gen',
#      'agiculture',
#      'agriforestryresource',
#      'ast0-0',
#      'ast0-0city',
#      'ast0-1',
#      'ast0-2',
#      'ast0-3',
#      'ast1-0',
#      'ast1-0b',
#      'ast1-2',
#      'ast1-3',
#      'ast1-4',
#      'ast1-5',
#      'ast2',
#      'ast2-0',
#      'ast2-0city',
#      'ast2-1',
#      'ast2-2',
#      'ast2-3',
#      'ast2-4',
#      'ast2-5',
#      'ast3',
#      'ast3-0',
#      'ast3-2',
#      'ast4',
#      'ast4-0',
#      'ast4-0city',
#      'ast4-1',
#      'ast4-2',
#      'ast4-cbdatabase',
#      'ast5',
#      'ast5-0',
#      'ast5-0city',
#      'ast5-1',
#      'ast6',
#      'ast6-0',
#      'ast6-0city',
#      'ast6-2',
#      'atmosphere',
#      'atmosphereresource',
#      'baltic',
#      'biodiversity',
#      'biodiversityresource',
#      'bsr3-1',
#      'bsr3-2',
#      'bsr3-3',
#      'bsr4-1',
#      'bsr4-2',
#      'bsr4-3',
#      'coastal',
#      'coastalresource',
#      'countr-area-urban',
#      'cryosphereresource',
#      'disaster risk',
#      'disasterresource',
#      'financial',
#      'financialresource',
#      'health',
#      'healthresource',
#      'ice',
#      'infra-res',
#      'infrastructure',
#      'mapset-ast-obsscen',
#      'mapset-ast-vulnrisk',
#      'marineresource',
#      'obs-scen-atm',
#      'obs-scen-cry',
#      'obs-scen-gen',
#      'obs-scen-sea',
#      'obs-scen-ter',
#      'obs-scen-urb',
#      'obs-scen-wat',
#      'org1-global',
#      'org2-europe',
#      'urban',
#      'urbanresource',
#      'vuln-risk-gen',
#      'water',
#      'waterresource'])

# aceitemtype is on of:
# set(['ACTION',
#      'DOCUMENT',
#      'GUIDANCE',
#      'INDICATOR',
#      'INFORMATIONSOURCE',
#      'MAPGRAPHDATASET',
#      'MEASURE',
#      'NULL_VALUE',
#      'ORGANISATION',
#      'TOOL'])
#


# countries is one of:
# set([None,
#      'AT',
#      'BE',
#      'BG',
#      'CH',
#      'CY',
#      'DE',
#      'DK',
#      'EE',
#      'ES',
#      'FI',
#      'FR',
#      'GB',
#      'GR',
#      'HU',
#      'IE',
#      'IS',
#      'IT',
#      'LI',
#      'LT',
#      'LU',
#      'LV',
#      'MT',
#      'NL',
#      'NO',
#      'NULL_VALUE',
#      'PL',
#      'PT',
#      'RO',
#      'SE',
#      'SI',
#      'SK',
#      'TR'])
