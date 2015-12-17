""" Importing utils
"""

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from collections import defaultdict
from collective.cover.tiles.configuration import TilesConfigurationScreen
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
#logger.addHandler(logging.StreamHandler())


ACE_ITEM_TYPES = {
    'DOCUMENT': 'eea.climateadapt.publicationreport',
    'INFORMATIONSOURCE': 'eea.climateadapt.informationportal',
    'GUIDANCE': 'eea.climateadapt.guidancedocument',
    'TOOL': 'eea.climateadapt.tool',
    'ORGANISATION': 'eea.climateadapt.organisation',
    'INDICATOR': 'eea.climateadapt.indicator',
    'MAPGRAPHDATASET': 'eea.climateadapt.mapgraphdataset',
    'RESEARCHPROJECT': 'eea.climateadapt.researchproject',
    'ACTION': 'eea.climateadapt.action',
}


def createAndPublishContentInContainer(*args, **kwargs):
    """ Wrap createContentInContainer and publish it """

    content = createContentInContainer(*args, **kwargs)
    wftool = getToolByName(content, "portal_workflow")

    if args[1] not in ('File', 'Image',):
        try:
            wftool.doActionFor(content, 'publish')
        except WorkflowException:
            # a workflow exception is risen if the state transition is not available
            # (the sampleProperty content is in a workflow state which
            # does not have a "submit" transition)
            logger.exception("Could not publish:" + content)

    return content


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
        'sortBy': 'sortBy',

        'css_class': 'css_class',
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
        payload.update({'css_class': 'col-md-4'})
        return make_aceitem_search_tile(cover, payload)
    else:
        payload.update({'css_class': 'col-md-4'})
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


def set_css_class(cover, tile, css_class):
    if css_class:
        tile_conf_adapter = TilesConfigurationScreen(cover, None, tile)

        conf = tile_conf_adapter.get_configuration()
        conf['css_class'] = css_class
        tile_conf_adapter.set_configuration(conf)



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

    css_class = info.pop('css_class', None)

    ITileDataManager(tile).set(info)

    set_css_class(cover, tile, css_class)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_transregion_dropdown_tile(cover):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.transregionselect'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    ITileDataManager(tile).set({'title': u"Trans regional select"})

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_ast_navigation_tile(cover):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.ast_navigation'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    ITileDataManager(tile).set({'title': u"AST Navigation"})

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_countries_dropdown_tile(cover):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.countryselect'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    ITileDataManager(tile).set({'title': u"Country select"})

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

    css_class = info.pop('css_class', None)
    ITileDataManager(tile).set(info)

    # TODO: relevant stuff here
    # info = _clean_portlet_settings(payload)
    # if filter(lambda x: x.startswith('user'), payload.keys()):
    #     return make_aceitem_relevant_content_tile(cover, payload)

    set_css_class(cover, tile, css_class)

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

    content['text'] = unicode(fix_links(site, unicode(content['text'])))
    content['title'] = unicode(content['title'])

    css_class = content.pop('css_class', None)

    ITileDataManager(tile).set(content)

    set_css_class(cover, tile, css_class)

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

    css_class = content.pop('css_class', None)

    ITileDataManager(tile).set(content)

    set_css_class(cover, tile, css_class)

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

    css_class = content.pop('css_class', None)

    ITileDataManager(tile).set(content)

    set_css_class(cover, tile, css_class)

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


def make_group(size=12, *tiles):
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
            parent = createAndPublishContentInContainer(
                parent,
                'Folder',
                title=name,
            )
        else:
            parent = parent[name]

    cover = createAndPublishContentInContainer(
        parent,
        'collective.cover.content',
        id=id,
        **kw
    )
    logger.info("Created new cover at %s", cover.absolute_url(1))

    return cover


def log_call(wrapped):
    def wrapper(*args, **kwargs):
        logger.debug("Calling %s", wrapped.func_name)
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


def get_param_from_link(text, param='uuid'):
    link = urlparse.urlparse(text)
    d = urlparse.parse_qs(link.query)
    if param in d:
        return d[param][0]


def get_image_from_link(site, link):
    """ Returns a Plone image object by extracting needed info from a link
    """
    # a link can have either uuid or img_id

    if "@@images" in link:
        return link     # this is already a Plone link

    uuid = get_param_from_link(link, 'uuid')
    if uuid:
        return get_repofile_by_uuid(site, uuid)

    try:
        # some links are like: /documents/18/11231805/urban_ast_step0.png/38b047f5-65be-4fcd-bdd6-3bd9d52cd83d?t=1411119161497
        uuid = UUID_RE.search(link).group()
        return get_repofile_by_uuid(site, uuid)
    except Exception:
        pass

    image_id = get_param_from_link(link, 'img_id')
    if image_id:
        return get_image_by_imageid(site, image_id)

    return link     #TODO: put the error back
    raise ValueError("Image not found for link: {0}".format(link))


def localize(obj, site):
    # returns the path to an object localized to the website
    path = obj.getPhysicalPath()
    site_path = site.getPhysicalPath()
    return '/' + '/'.join(path[len(site_path):])


def fix_inner_link(site, href):

    href = href.strip()

    # TODO: fix links like:
    #     /viewaceitem?aceitem_id=8434
    #     /viewmeasure?ace_measure_id=1102
    # http://climate-adapt.eea.europa.eu/viewmeasure?ace_measure_id=3311
    # http://climate-adapt.eea.europa.eu/web/guest/uncertainty-guidance/topic2?p_p_id=56_INSTANCE_qWU5&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1#How+are+uncertainties+quantified%3F
    # http://localhost:8001/Plone/repository/11245406.jpg/@@images/image
    # http://climate-adapt.eea.europa.eu/projects1?ace_project_id=55


    starters = [
        'http://climate-adapt.eea.europa.eu/',
        '../../../',
        '/web/guest/', '/'
    ]
    for path in starters:
        if href.startswith(path):
            href = href.replace(path, '/', 1)

    if "/viewmeasure" in href:
        acemeasure_id = get_param_from_link(href, 'ace_measure_id')
        obj = _get_imported_acemeasure(site, acemeasure_id)
        if obj:
            return localize(obj, site)

    if "/viewaceitem" in href:
        aceitem_id = get_param_from_link(href, 'aceitem_id')
        obj = _get_imported_aceitem(site, aceitem_id)
        if obj:
            return localize(obj, site)

    uuid = get_param_from_link(href, 'uuid')
    if uuid:
        return get_repofile_by_uuid(site, uuid)

    try:
        # some links are like: /documents/18/11231805/urban_ast_step0.png/38b047f5-65be-4fcd-bdd6-3bd9d52cd83d?t=1411119161497
        uuid = UUID_RE.search(href).group()
        return get_repofile_by_uuid(site, uuid)
    except Exception:
        logger.debug("Couldn't find proper equivalent link for %s", href)
        return href

    return href


def fix_links(site, text):

    f = open('/tmp/links.txt', 'a+')

    from lxml.html.soupparser import fromstring
    e = fromstring(text)

    for img in e.xpath('//img'):
        src = img.get('src')
        f.write((src or '').encode('utf-8') + "\n")

        image = get_image_from_link(site, src)

        if isinstance(image, basestring):
            pass
        else:
            if image is not None:
                url = localize(image, site) + "/@@images/image"
                logger.info("Change image link %s to %s", src, url)
                img.set('src', url)

    for a in e.xpath('//a'):
        href = a.get('href')
        f.write((href or '').encode('utf-8') + "\n")
        if href is not None:
            new_href = fix_inner_link(site, href)
            if href != new_href:
                logger.info("Change link %s to %s", href, new_href)
            a.set('href', href)

    f.close()
    return lxml.html.tostring(e, encoding='unicode', pretty_print=True)


UUID_RE = re.compile(
    "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)

def get_image_by_imageid(site, imageid):
    #import pdb; pdb.set_trace()
    repo = site['repository']
    reg = re.compile(str(imageid) + '.[jpg|png]')

    ids = [m.string for m in [reg.match(cid) for cid in repo.contentIds()] if m]

    if len(ids) != 1:
        # we will try to find it by uuid
        from eea.climateadapt._importer import session
        from eea.climateadapt._importer import sql
        uuid = session.query(sql.Dlfileentry.uuid_
                             ).filter_by(largeimageid=imageid).one()[0]
        return get_repofile_by_uuid(site, uuid)

    return repo[ids[0]]


def get_repofile_by_uuid(site, uuid):
    catalog = site['portal_catalog']
    return catalog.searchResults(imported_uuid=uuid)[0].getObject()


MAP_OF_OBJECTS = defaultdict(lambda:{})
ACEMEASURE_TYPES = ['eea.climateadapt.casestudy',
                    'eea.climateadapt.adaptationoption',]


def _get_imported_aceitem(site, id):
    coll = MAP_OF_OBJECTS['aceitems']
    if len(coll) == 0:
        for pt in ACE_ITEM_TYPES.values():
            brains = site.portal_catalog.searchResults(portal_type=pt)
            for b in brains:
                obj = b.getObject()
                coll[obj._aceitem_id] = obj

    try:
        return coll[long(id)]
    except:
        logger.warning("Could not find aceitem with id %s", id)
        return


def _get_imported_aceproject(site, id):
    pt = "eea.climateadapt.aceproject"
    coll = MAP_OF_OBJECTS['aceprojects']
    if len(coll) == 0:
        brains = site.portal_catalog.search_results(portal_type=pt)
        for b in brains:
            obj = b.getObject()
            coll[obj._aceproject_id] = obj

    try:
        return coll[long(id)]
    except:
        logger.warning("Could not find aceproject with id %s", id)
        return


def _get_imported_acemeasure(site, id):
    coll = MAP_OF_OBJECTS['acemeasures']
    if len(coll) == 0:
        for pt in ACEMEASURE_TYPES:
            brains = site.portal_catalog.searchResults(portal_type=pt)
            for b in brains:
                obj = b.getObject()
                coll[obj._acemeasure_id] = obj

    try:
        return coll[long(id)]
    except:
        logger.warning("Could not find acemeasure with id %s", id)
        return


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
