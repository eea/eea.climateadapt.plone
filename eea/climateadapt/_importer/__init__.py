#from plone.app.textfield import RichTextValue
#from pprint import pprint
from collections import defaultdict
from eea.climateadapt._importer import sqlschema as sql
from eea.climateadapt._importer.utils import SOLVERS
from eea.climateadapt._importer.utils import parse_settings, s2l    #, printe
from eea.climateadapt._importer.utils import strip_xml
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUIDGenerator
from sqlalchemy import Column, BigInteger, String, Text, DateTime   #, text
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from zope.component import getUtility
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.sqlalchemy import register
import json
import logging
import lxml.etree
import os
import re
import sys
import transaction


logger = logging.getLogger('eea.climateadapt.importer')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

session = None      # this will be a global bound to the current module

MAPOFLAYOUTS = defaultdict(list)

RELATIONS = {
    'Addres': {
        'company': {'other': 'Company', 'fk': 'companyid', 'bref': 'addresses'},
        'user': {'other': 'User', 'fk': 'userid', 'bref': 'addresses'},
        'region': {'other': 'Region', 'fk': 'regionid', 'bref': 'addresses'},
        'country': {'other': 'Country', 'fk': 'countryid', 'bref': 'addresses'},
        #'type_': {'other': 'Type', 'fk': 'typeid', 'bref': 'addresses'},
    },
    'Account': {    # count: 2
        'company': {'other': 'Company', 'fk': 'companyid', 'bref': 'accounts'},
        'user': {'other': 'User', 'fk': 'userid', 'bref': 'account'}
    },
    'AceAceitem': { # count: 1762
        'company': {'other': 'Company', 'fk': 'companyid', 'bref': 'aceitems'},
    },
    'AceMeasure': { # count: 150
        'company': {'other': 'Company', 'fk': 'companyid', 'bref': 'acemeasures'},
        'group': {'other': 'Group', 'fk': 'groupid', 'bref': 'acemeasures'},
    },
    'AceProject': { # count: 418
        'company': {'other': 'Company', 'fk': 'companyid', 'bref': 'aceprojects'},
        'group': {'other': 'Group', 'fk': 'groupid', 'bref': 'aceprojects'},
    },
    'Assetentry': { # count: 15673
        'company': {'other': 'Company', 'fk': 'companyid', 'bref': 'assetentries'},
        'group': {'other': 'Group', 'fk': 'groupid', 'bref': 'assetentries'},
        'user': {'other': 'User', 'fk': 'userid', 'bref': 'assetentries'},
        'classname': {'other': 'Classname', 'fk': 'classnameid', 'bref': 'usedby_assetentry'},
        # classpk bigint,
        # classuuid character varying(75),
        # classtypeid bigint,
        # layoutuuid character varying(75),
    },
    # climwat_exc ??? looks like an excel sheet
    # Country
    # TODO: files (aka dlfileentry)
    'User': {       # count: 12504
        'contact': {'other': 'Contact', 'fk': 'contactid', 'bref': 'user'},
        'company': {'other': 'Company', 'fk': 'companyid', 'bref': 'users'},
    },
    'Group': {
        'company': {'other': 'Company', 'fk': 'companyid', 'bref': 'groups'},
        # 'creator': {'other': 'User', 'fk': 'creatoruserid', 'bref': 'groups_created'},
        'classname': {'other': 'Classname', 'fk': 'classnameid', 'bref': 'usedby_groups'},
    },
    'Journalarticle': { # count: 4203
        'company': {'other': 'Company', 'fk': 'companyid', 'bref': 'journalarticles'},
        'group': {'other': 'Group', 'fk': 'groupid', 'bref': 'journalarticles'},
        'user': {'other': 'User', 'fk': 'userid', 'bref': 'journalarticles'},
        'classname': {'other': 'Classname', 'fk': 'classnameid', 'bref': 'usedby_journalarticle'},
    },
    'Journalarticleimage': { # count: 1056
        'article': {'other': 'Journalarticle', 'fk': 'articleid', 'bref': 'images'},
    },
    'Journalarticleresource': { # count: 669
        'article': {'other': 'Journalarticle', 'fk': 'articleid', 'bref': 'resources'},
        'group': {'other': 'Group', 'fk': 'groupid', 'bref': 'journalresources'},
    },

    # kaleo* - workflow history status
    # mb* - comments - can't find "meat" of the comments

    # TODO: users_groups to be used to map users to groups. users_usergroups???
    #       users_roles, same

}


class AceIndicator(sql.Base):   # count: 42
    __tablename__ = 'ace_indicator'

    # aceindicatorid = Column(BigInteger, primary_key=True,
    #                         server_default=text("nextval('ace_indicator_id_seq'::regclass)"))

    aceitemid = Column('aceitemid', BigInteger, primary_key=True)
    aceitem = relationship(sql.AceAceitem,
                           foreign_keys="ace_indicator.c.aceitemid",
                           backref='aceindicator',
                           primaryjoin="and_(AceAceitem.aceitemid==AceIndicator.aceitemid)")

    companyid = Column('companyid', BigInteger)
    groupid = Column('groupid', BigInteger)
    nasid = Column('nasid', BigInteger)
    name = Column('name', String(255))
    description = Column('description', Text)
    datatype = Column('datatype', String(255))
    storedat = Column('storedat', String(255))
    storagetype = Column('storagetype', String(255))
    language = Column('language', String(24))
    textsearch = Column('textsearch', Text)
    keyword = Column('keyword', String(2048))
    targetresolution = Column('targetresolution', String(255))
    spatiallayer = Column('spatiallayer', String(150))
    spatialvalues = Column('spatialvalues', String(255))
    startdate = Column('startdate', DateTime)
    enddate = Column('enddate', DateTime)
    publicationdate = Column('publicationdate', DateTime)
    sectors_ = Column('sectors_', String(255))
    elements_ = Column('elements_', String(255))
    climateimpacts_ = Column('climateimpacts_', String(255))
    rating = Column('rating', BigInteger)
    importance = Column('importance', BigInteger)

sql.AceIndicator = AceIndicator

ACE_ITEM_TYPES = {
    'DOCUMENT': 'eea.climateadapt.publicationreport',
    'INFORMATIONSOURCE': 'eea.climateadapt.informationportal',
    'GUIDANCE': 'eea.climateadapt.guidancedocument',
    'TOOL': 'eea.climateadapt.tool',
    'ORGANIZATION': 'eea.climateadapt.organization'
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

@log_call
def import_aceitem(data, location):
    # TODO: Some AceItems have ACTION, MEASURE, REASEARCHPROJECT types and
    # should be mapped over AceMeasure and AceProject

    if data.datatype in ACE_ITEM_TYPES:
        item = createContentInContainer(
            location,
            ACE_ITEM_TYPES[data.datatype],
            title=data.name,
            description=data.description,
            keywords=data.keyword,
            spatial_layer=data.spatiallayer,
            data_type=s2l(data.datatype),
            storage_type=s2l(data.storagetype),
            sectors=s2l(data.sectors_),
            elements=s2l(data.elements_),
            climate_impacts=s2l(data.climateimpacts_),
            source=data.source,
            comments=data.comments,
            year=data.year,
            geochars=data.geochars
        )

        logger.info("Imported aceitem %s from sql aceitem %s",
                    item, data.aceitemid)
        return item
    else:
        raise ValueError("You missed an acetype item")


@log_call
def import_aceproject(data, location):
    item = createContentInContainer(
        location,
        'eea.climateadapt.aceproject',
        title=data.title,
        acronym=data.acronym,
        lead=data.lead,
        website=data.website,
        abstracts=data.abstracts,
        source=data.source,
        partners=data.partners,
        keywords=data.keywords,
        sectors=s2l(data.sectors),
        elements=s2l(data.element),
        climate_impacts=s2l(data.climateimpacts),
        funding=data.funding,
        duration=data.duration,
        specialtagging=data.specialtagging,
        geochars=data.geochars,
        countries=s2l(data.spatialvalues),
        comments=data.comments,
    )

    logger.info("Imported aceproject %s from sql aceproject %s",
                item, data.projectid)

    return item


@log_call
def import_adaptationoption(data, location):
    item = createContentInContainer(
        location,
        'eea.climateadapt.adaptationoption',
        title=data.name,
        implementation_type=data.implementationtype,
        implementation_time=data.implementationtime,
        lifetime=data.lifetime,
        spatial_layer=data.spatiallayer,
        spatial_values=data.spatialvalues,
        legal_aspects=data.legalaspects,
        stakeholder_participation=data.stakeholderparticipation,
        contact=data.contact,
        success_limitations=data.succeslimitations,
        cost_benefit=data.costbenefit,
        websites=s2l(data.website),
        sectors=s2l(data.sectors_),
        elements=s2l(data.elements_),
        climate_impacts=s2l(data.climateimpacts_),
        source=data.source,
        geochars=data.geochars,
        measure_type=data.mao_type,
        comments=data.comments,
    )

    logger.info("Imported aceproject %s from sql aceitem %s",
                item, data.measureid)

    return item


@log_call
def import_casestudy(data, location):
    item = createContentInContainer(
        location,
        'eea.climateadapt.casestudy',
        title=data.name,
        implementation_type=data.implementationtype,
        implementation_time=data.implementationtime,
        lifetime=data.lifetime,
        spatial_layer=data.spatiallayer,
        spatial_values=data.spatialvalues,
        legal_aspects=data.legalaspects,
        stakeholder_participation=data.stakeholderparticipation,
        contact=data.contact,
        success_limitations=data.succeslimitations,
        cost_benefit=data.costbenefit,
        websites=s2l(data.website),
        sectors=s2l(data.sectors_),
        elements=s2l(data.elements_),
        climate_impacts=s2l(data.climateimpacts_),
        location_lat=data.lat,
        location_lon=data.lon,
        source=data.source,
        geochars=data.geochars,
        measure_type=data.mao_type,
        comments=data.comments,
    )

    logger.info("Imported casestudy %s from sql acemeasure %s",
                item, data.measureid)

    return item

@log_call
def import_image(data, location):
    try:
        name = str(data.imageid) + '.' + data.type_ + '/1.0'
        file_data = open('./document_library/0/0/' + name).read()
    except Exception:
        logger.warning("Image with id %d does not exist in the supplied "
                       "document library", data.imageid)
        return None

    item = createContentInContainer(
        location,
        'Image',
        title='Image ' + str(data.imageid),
        id=str(data.imageid) + '.' + data.type_,
        image=NamedBlobImage(
            filename=str(data.imageid) + data.type_,
            data=file_data
        )
    )

    logger.info("Imported image %s from sql Image %s", item, data.imageid)

    return item


@log_call
def import_dlfileentry(data, location):
    try:
        file_data = open('./document_library/' + str(data.companyid) + '/' +
                         str(data.folderid or data.groupid) + '/' + str(data.name) +
                         '/' + data.version).read()
    except Exception:
        logger.warning("File with id %d and title '%s' does not exist in the "
                       "supplied document library", data.fileentryid,
                       data.title)
        return None

    if 'jpg' in data.extension or 'png' in data.extension:
        item = createContentInContainer(
            location,
            'Image',
            title=data.title,
            description=data.description,
            id=str(data.name) + '.' + data.extension,
            image=NamedBlobImage(
                filename=str(data.name) + '.' + data.extension,
                data=file_data
            )
        )
    else:
        item = createContentInContainer(
            location,
            'File',
            title=data.title,
            description=data.description,
            id=str(data.name) + '.' + data.extension,
            file=NamedBlobFile(
                filename=str(data.name) + '.' + data.extension,
                data=file_data
            )
        )

    logger.info("Imported %s from sql dlentry %s", item, data.fileentryid)

    return item


def _get_portlet(portletid, layout):
    """ Get the portlet based on portletid and layout.plid

    layout.plid is the "portlet instance id" """
    try:
        portlet = session.query(sql.Portletpreference).filter_by(
            portletid=portletid, plid=layout.plid,
        ).one()
        return portlet
    except:
        return None


def _get_article_for_portlet(portlet):
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


def extract_portlet_info(portletid, layout):
    """ Extract portlet information from the portlet with portletid

    The result can vary, based on what we find in a portlet.

    It can be:
        * a simple string with text
        * a list of ('type_of_info', info)
    """
    portlet = _get_portlet(portletid, layout)
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
        name = pref.find('name').text
        value = pref.find('value')
        try:
            value = value.text
        except Exception:
            pass
        prefs[name] = value

    portlet_title = None
    if prefs.get('portletSetupUseCustomTitle') == "true":
        for k, v in prefs.items():
            if k.startswith('portletSetupTitle'):
                portlet_title = v

    article = _get_article_for_portlet(portlet)
    if article is not None:
        e = lxml.etree.fromstring(article.content.encode('utf-8'))

        # TODO: attach other needed metadata
        return {'title': article.title,
                'description': article.description,
                'content': [SOLVERS[child.tag](child) for child in e],
                'portlet_title': portlet_title
                }

    logger.debug("Could not get an article from portlet %s for %s",
                    portletid, layout.friendlyurl)

    return prefs


no_import_layouts = [
    '/documents',   # this is an internal Liferay page
    '/contact-us',  # this is a page that doesn't really exist in the db
    '/climate-hazards',  # this is a page that doesn't really exist in the db
    '/adaptation-sectors',  # this is a page that doesn't really exist in the db
    '/good-practices',
    '/news-and-forum',
    '/general',
    '/national-adaptation-strategies',
    '/european-sector-policy',
    '/tools/dgregio2020',  # doesn't display anything
    '/mars-viewer',
    '/projects1',
    '/5',
    '/viewmeasure',
    '/viewaceitem',
    '/cities-map',
    '/city',
]

portlet_importers = {   # import specific portlets by their ID
    # TODO: implement this importer. It sits at page http://adapt-test.eea.europa.eu/data-and-downloads
    'acesearchportlet_WAR_AceItemportlet': lambda layout, structure: None
}


@log_call
def import_layout(layout, site):
    # import layout as folder
    # create documents for each portlet in 'typesettings':
    # u'sitemap-changefreq=daily\nlayout-template-id=2_columns_iii\nsitemap-include=1\ncolumn-2=56_INSTANCE_9tMz,\ncolumn-1=56_INSTANCE_2cAx,56_INSTANCE_TN6e,\n'
    # split content from layout template
    # search for portlet name in portletpreferences
    # parse the prefs and look for articleid
    # create page from journalarticle

    if layout.friendlyurl in no_import_layouts:
        return

    if layout.type_ == u'control-panel':
        # we skip control panel pages
        return

    settings = parse_settings(layout.typesettings)

    if layout.type_ == u'link_to_layout':
        # TODO: this is a shortcut link should create as a folder and add the linked layout as default page
        #linked_layoutid = settings['linkToLayoutId']
        return

    template = settings['layout-template-id'][0]
    MAPOFLAYOUTS[template].append(layout.friendlyurl)
    #print layout.type_, "\t\t", template, "\t\t", layout.friendlyurl

    logger.info("Importing layout %s at url %s with template %s",
                layout.uuid_, layout.friendlyurl, template)

    is_column = lambda s: (s.startswith('column-')
                           and not s.endswith('-customizable'))

    structure = {}

    structure['name'] = strip_xml(layout.name)

    for column, portlet_ids in filter(lambda kv: is_column(kv[0]),
                                      settings.items()):
        structure[column] = []   # a column is a list of portlets
        for portletid in portlet_ids:
            content = extract_portlet_info(portletid, layout)
            structure[column].append((portletid, content))

    importer = globals().get('import_template_' + template)
    importer(site, layout, structure)


# possible templates are
# [u'1_2_1_columns', u'1_2_columns_i', u'1_2_columns_ii', u'1_column',
# u'2_columns_i', u'2_columns_ii', u'2_columns_iii', u'ace_layout_1',
# u'ace_layout_2', u'ace_layout_3', u'ace_layout_4', u'ace_layout_5',
# u'ace_layout_col_1_2', u'ast', u'faq', u'frontpage', u'transnationalregion',
# u'urban_ast']

def make_richtext_tile(context, content):
    # creates a new tile and saves it in the annotation
    # returns a python objects usable in the layout description

    id = getUtility(IUUIDGenerator)()
    typeName = 'collective.cover.richtext'
    tile = context.restrictedTraverse('@@%s/%s' % (typeName, id))

    ITileDataManager(tile).set({'text': content})

    return {
        'tile-type': 'collective.cover.richtext',
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


def get_image(site, imageid):
    repo = site['repository']
    reg = re.compile(str(imageid) + '.[jpg|png]')

    ids = [m.string for m in [reg.match(cid) for cid in repo.contentIds()] if m]

    if len(ids) == 1:
        raise ValueError("Image {} not found in repository".format(imageid))

    return repo[ids[0]]


def make_image_tile(site, cover, info):
    id = getUtility(IUUIDGenerator)()
    type_name =  'collective.cover.banner'
    tile = cover.restrictedTraverse('@@%s/%s' % (type_name, id))

    imageid = info['id']
    image = get_image(site, imageid)
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

def render(path, options):
    tpl = PageTemplateFile(path, globals())
    ns = tpl.pt_getContext((), options)
    return tpl.pt_render(ns)


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


@log_call
def import_template_1_2_1_columns(site, layout, structure):
    # column-1 has a table with links and a table with info
    # column-2 has an iframe
    # Only one page: http://adapt-test.eea.europa.eu//tools/urban-adaptation/my-adaptation

    assert(len(structure) == 3)
    assert(len(structure['column-1']) == 2)
    assert(len(structure['column-2']) == 1)

    nav = structure['column-1'][0][1]['content'][0]
    text = structure['column-1'][1][1]['content'][0]
    iframe = structure['column-2'][0][1]['url']

    cover = create_cover_at(site, layout.friendlyurl,
                            title=str(structure['name']))

    layout = [{'type': 'row', 'children': []}]

    nav_tile = make_richtext_tile(cover, nav)
    text_tile = make_richtext_tile(cover, text)
    iframe_tile = make_iframe_embed_tile(cover, iframe)

    # we create 3 rows, each with a separate tile

    layout = make_layout([make_row(make_group(tile))
                          for tile in (nav_tile, text_tile, iframe_tile) ])

    layout = json.dumps(layout)

    cover.cover_layout = layout
    # cover._p_changed = True


@log_call
def import_template_transnationalregion(site, layout, structure):
    # a country page is a structure with 3 "columns":
    # column-1 has an image and a select box to select other countries
    # column-2 has is a structure of tabs and tables
    # column-3 is unknown and will be ignored
    # Ex: /countries/liechtenstein

    assert(len(structure) >= 2)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-2']) == 1)

    payload = structure['column-2'][0]
    portletid, records = payload
    country = {'Summary': []}
    tabs = []

    for record in records['content']:
        type_, id, payload = record
        if type_ == 'text':
            country[id] = payload[0]
            tabs.append(id)
        if type_ == 'dynamic':
            for info in record[2]:
                if isinstance(info, basestring):
                    continue
                t, name, text = info
                country['Summary'].append((name, text[0]))
                if 'Summary' not in tabs:
                    tabs.append('Summary')

    column1_content = structure['column-1'][0]
    portletid, records = column1_content
    image_info = {
        'id': records['content'][0][2][0],
        'description': records['description'],
        'title': records['title'],
    }
    country['image'] = image_info
    country['name'] = structure['name']

    table = pack_to_table(country['Summary'])
    country['Summary'] = render('templates/table.pt', table)

    payload = []
    for tab in tabs:
        payload.append((tab, country[tab]))

    main_content = render('templates/accordion.pt', {'payload': payload})

    cover = create_cover_at(site, layout.friendlyurl)

    image_tile = make_image_tile(site, cover, image_info)    # TODO: import image
    content_tile = make_richtext_tile(cover, main_content)

    image_group = make_group(2, image_tile)
    content_group = make_group(14, content_tile)

    layout = make_layout(make_row(image_group, content_group))
    cover.cover_layout = json.dumps(layout)
    cover._p_changed = True


@log_call
def import_template_ace_layout_2(site, layout, structure):
    # there are three pages for this layout
    # two of them are empty because there's another layout with redirection
    # the third one is at http://adapt-test.eea.europa.eu/adaptation-measures
    # and has 2 filter portlet and a simple filter portlet

    if not structure.get('column-2') or len(structure['column-2'][0][1]) == 0:
        # this is a redirection layout, will be created in another place
        return

    assert(len(structure) == 5)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-2']) == 1)
    assert(len(structure['column-3']) == 1)
    assert(len(structure['column-4']) == 1)

    image = structure['column-1'][0][1]['content'][0][2]
    title = structure['column-1'][0][1]['content'][1][2][0]
    body = structure['column-1'][0][1]['content'][2][2][0]
    readmore = structure['column-1'][0][1]['content'][3][2][0]

    col2_portlet = structure['column-2'][0][1]
    col3_portlet = structure['column-3'][0][1]
    col4_portlet = structure['column-4'][0][1]

    return noop(layout, image, title, body, readmore, col2_portlet,
                col3_portlet, col4_portlet)


@log_call
def import_template_ace_layout_col_1_2(site, layout, structure):
    # this is a 2 column page with some navigation on the left and a big
    # iframe (or just plain html text) on the right
    # example page: http://adapt-test.eea.europa.eu//tools/urban-adaptation/climatic-threats/heat-waves/sensitivity
    assert(len(structure) == 3)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-3']) == 1)

    title = strip_xml(structure['name'])
    main = structure['column-3'][0][1].get('url')
    if not main:
        main = ('text', structure['column-3'][0][1]['content'][0])
    else:
        main = ('iframe', main)

    nav_menu = structure['column-1'][0][1]['content'][0]    # TODO: fix nav menu links
    noop(layout, title, main, nav_menu)


@log_call
def import_template_ace_layout_3(site, layout, structure):
    # this is a "details" page, ex: http://adapt-test.eea.europa.eu/transnational-regions/baltic-sea/policy-framework
    # main column has an image, title, main text and "read more text"
    # sidebar has a aceitem search portlet
    # extra, there is an id for a tab based navigation, as a separate column
    # called 'name'
    # some pages may contain extra columns under the main column

    main = {}
    for line in structure['column-1'][0][1]['content']:
        if line[0] == 'image':
            main['image'] = line[2][0]
            continue
        if line[0] == 'dynamic' and line[1] == 'Title':
            main['title'] = line[2][0]
            continue
        if line[0] == 'text' and line[1] == 'Body':
            main['body'] = line[2][0]
        if line[0] == 'text' and line[1] == 'ReadMoreBody':
            main['readmore'] = line[2][0]
    search_portlet = structure['column-5']
    name = structure['name']

    extra_columns = {}
    keys = ['column-2', 'column-3', 'column-4']
    for key in keys:
        if key in structure:
            if 'portletSetupTitle_en_GB' in structure[key][0][1]:
                column_name = structure[key][0][1]['portletSetupTitle_en_GB']
                extra_columns[column_name] = structure[key]
            else:
                extra_columns['Multimedia'] = structure[key]

    noop(layout, main, search_portlet, extra_columns, name)


@log_call
def import_template_ace_layout_4(site, layout, structure):
    # these are Project pages such as http://adapt-test.eea.europa.eu/web/guest/project/climsave
    main = {
        'accordion': [],
    }
    partners = []
    for line in structure['column-1'][0][1]['content']:
        if line[0] == 'image':
            main['image'] = line[2][0]
            continue
        if line[0] == 'dynamic' and line[1] == 'Subtitle':
            main['subtitle'] = line[2][0]
            continue
        if line[0] == 'dynamic' and line[1] == 'Title':
            main['title'] = line[2][0]
            continue
        if line[0] == 'text':
            category = line[1]
            text = line[2][0]
            main['accordion'].append((category, text))
            continue
        if line[0] == 'dynamic' and line[1] == 'ProjectPartner':
            name = line[2][0][2][0]
            symbol = line[2][1][2][0]
            if name:
                partners.append((name, symbol))

    main['accordion'].append(('ProjectPartners', partners))

    _main_sidebar = structure['column-2'][0][1]['content']
    sidebar = []
    for line in _main_sidebar:
        if line[1] != 'Contact':
            sidebar.append((line[1], line[2][0]))
        else:
            contact = []
            for subline in line[2]:
                if not subline:
                    continue
                contact.append((subline[1], subline[2][0]))
            sidebar.append(contact)

    if len(structure['column-2']) > 1:
        for portlet in structure['column-2'][1:]:
            sidebar.append(('extratext', portlet[1]['content'][0]))

    noop(layout, main, sidebar)


@log_call
def import_template_ast(site, layout, structure):
    # TODO: create ast page based on structure
    # column-1 has the imagemap on the left side
    # column-2 has 2 portlets:  title and then the one with content (which also
    # has a title)
    assert(len(structure) >= 3)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-2']) >= 2)

    image_portlet = structure['column-1'][0][1]['content'][0]
    header_text = structure['column-2'][0][1]['headertext']
    content = structure['column-2'][1][1]['content'][0]

    content_portlet = None
    if len(structure['column-2']) > 2:
        assert(len(structure['column-2']) == 3)
        content_portlet = structure['column-2'][2]

    extra_columns = {}
    [structure.pop(x) for x in ('name', 'column-1', 'column-2')]
    for key in structure:
        portlet_name = structure[key][0][1]['portletSetupTitle_en_GB']
        extra_columns[portlet_name] = structure[key]

    noop(image_portlet, header_text, content, content_portlet, extra_columns)


@log_call
def import_template_urban_ast(site, layout, structure):
    # TODO: create urbanast page based on structure
    # column-1 has the imagemap on the left side
    # column-2 has 2 portlets:  title and then the one with content (which also
    # has a title)
    assert(len(structure) >= 3)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-2']) >= 2)

    image_portlet = structure['column-1'][0][1]['content'][0]
    header_text = structure['column-2'][0][1]['headertext']
    content = structure['column-2'][1][1]['content'][0]

    content_portlet = None
    if len(structure['column-2']) > 2:
        assert(len(structure['column-2']) == 3)
        content_portlet = structure['column-2'][2]

    extra_columns = {}
    [structure.pop(x) for x in ('name', 'column-1', 'column-2')]
    for key in structure:
        if 'portletSetupTitle_en_GB' in structure[key][0][1]:
            portlet_name = structure[key][0][1]['portletSetupTitle_en_GB']
            extra_columns[portlet_name] = structure[key]
        else:
            assert(len(structure[key][0][1]) == 4)
            column_name = structure[key][0][1]['portlet_title']
            extra_columns[column_name] = structure[key][0][1]['content'][0]

    noop(layout, image_portlet, header_text, content, content_portlet,
         extra_columns)


@log_call
def import_template_1_2_columns_i(site, layout, structure):
    # TODO: column-1 - mapviewerportlet
    # TODO: column-2 and column-3 - simplefilterportlet
    # there's only one page, here: /map-viewer
    logger.warning("Please investigate this importer %s with template %s",
                   layout.friendlyurl, '1_2_columns_i')
    return


@log_call
def import_template_1_2_columns_ii(site, layout, structure):
    # ex page: /share-your-info/general
    # TODO: column02 contains sharemeasureportlet
    assert(len(structure) == 2 or len(structure) == 3)
    assert(len(structure['column-1']) == 1)
    if len(structure) > 2:
        assert(len(structure['column-2']) == 1)

    image = structure['column-1'][0][1]['content'][0][2][0]
    title = structure['column-1'][0][1]['content'][1][2][0]
    body = structure['column-1'][0][1]['content'][2][2][0]

    share_portlet = None
    if len(structure) == 3:
        share_portlet = structure['column-2'][0][1]

    noop(layout, image, title, body, share_portlet)


@log_call
def import_template_1_column(site, layout, structure):
    # this is a simple page, with one portlet of text
    # example: /eu-adaptation-policy/funding/life
    if structure['column-1'][0][0] in portlet_importers:
        importer = portlet_importers.get(structure['column-1'][0][0])
        return importer(layout, structure)

    assert len(structure) == 2  # main portlet + layout name

    try:
        dict(structure['column-1'][0][1])
    except:
        logger.warning("Invalid page structure for %s", layout.friendlyurl)
        return

    if not 'content' in structure['column-1'][0][1]:
        #TODO: import this properly
        logger.warning("Please investigate this importer %s with template %s",
                       layout.friendlyurl, '1_column')
        return

    try:
        content = structure['column-1'][0][1]['content']
    except:
        # TODO: /sitemap (the contents are missing)
        import pdb; pdb.set_trace()

    if len(structure['column-1']) == 2:
        try:
            content += structure['column-1'][1][1]['content']
        except:
            content += structure['column-1'][0][1]['content'][0]

    portlet_title = structure['column-1'][0][1].get('portlet_title')
    if portlet_title:
        title = portlet_title
    else:
        title = structure['column-1'][0][1]['title']

    if len(structure['column-1']) > 2:
        col1 = content
        col2 = structure['column-1'][1][1]['content']
        iframe = structure['column-1'][2][1]['url']
        noop(col1, col2, iframe)
    else:
        noop(title, content, structure)


@log_call
def import_template_2_columns_i(site, layout, structure):
    # ex: /countries
    # TODO: column-1 may contain countriesportlet
    assert(len(structure) == 2 or len(structure) == 3)
    if len(structure) == 3:
        countries_portlet = structure['column-1'][0][1]
        body = structure['column-2'][0][1]['content'][0]
        portlet_title = structure['column-2'][0][1]['portlet_title']
    else:
        countries_portlet = None
        body = structure['column-1'][0][1]['content'][0]
        portlet_title = structure['column-1'][0][1]['portlet_title']
    title = structure['name']

    noop(layout, title, portlet_title, body, countries_portlet)


@log_call
def import_template_2_columns_ii(site, layout, structure):
    # this pages will have to be manually recreated
    # ex: /home

    if layout.friendlyurl == '/observations-and-scenarios':
        return  # this is imported in another layout

    if len(structure) == 1: # this is a fake page. Ex: /adaptation-sectors
        logger.warning("Please investigate this importer %s with template %s",
                       layout.friendlyurl, '2_columns_ii')
        return

    first = [x[1] for x in structure.get('column-1', []) if x[1]]
    second = [x[1] for x in structure.get('column-2', []) if x[1]]

    if first and second:
        # this is the /mayors-adapt page
        noop('mayors-adapt')


@log_call
def import_template_2_columns_iii(site, layout, structure):
    # ex: /organizations
    assert(len(structure) == 2 or len(structure) == 3)

    body = structure['column-1'][0][1]['content'][0]
    portlet_title = structure['column-1'][0][1]['portlet_title']

    if len(structure['column-1']) == 4:
        # There is only one layout with this structure
        filter_portlet_1 = structure['column-1'][1]
        filter_portlet_2 = structure['column-1'][2]
        blue_button = structure['column-1'][3][1]['content'][0]
    elif len(structure['column-1']) == 2:
        body += structure['column-1'][1][1]['content'][0]

    if len(structure) == 3:
        # column-2 has a image
        assert(len(structure['column-2']) == 1)
        image = structure['column-2'][0][1]['content'][0]

    noop(layout, portlet_title, body)


@log_call
def import_template_ace_layout_1(site, layout, structure):
    # ex page: /home (may be just a mockup for home page)
    logger.warning("Please investigate this importer %s with template %s",
                   layout.friendlyurl, 'ace_layout_1')


@log_call
def import_template_ace_layout_5(site, layout, structure):
    # ex page: /transnational-regions/caribbean-area
    assert(len(structure) == 4)
    assert(len(structure['column-1']) == 1)

    image = structure['column-1'][0][1]['content'][0][2][0]
    _first = structure['column-2'][0][1]['content'][0][2][0]

    if len(structure['column-2'][0][1]['content']) == 2:
        _second = structure['column-2'][0][1]['content'][1][2][0]
        _first += _second

    # TODO: import portlet
    portlet = structure['column-3']
    text = _first
    noop(image, text, portlet)


@log_call
def import_template_faq(site, layout, structure):
    """ This is a template with a main body text and three columns of HTML
    underneath.
    Ex:/uncertainty-guidance-ai
    """
    assert(len(structure) == 5)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-2']) == 1)
    assert(len(structure['column-3']) == 1)
    assert(len(structure['column-4']) == 1)

    main_text = structure['column-1'][0][1]['content'][0]
    col1 = structure['column-2'][0][1]['content'][0]
    col2 = structure['column-3'][0][1]['content'][0]
    col3 = structure['column-4'][0][1]['content'][0]
    return noop(main_text, col1, col2, col3)


@log_call
def import_template_frontpage(site, layout, structure):
    # ex page: /home
    # TODO: column-1 home_slider_portlet
    # column-2 home_search_portlet
    # column-5 AceNews_WAR_HomeNewsEventportlet (News)
    # column-6 AceNews_WAR_HomeNewsEventportlet (Events)
    assert(len(structure) == 9)
    country_selector = structure['column-3'][0][1]['content'][0]
    share_info = structure['column-4'][0][1]['content'][0]
    sector_policies = structure['column-7'][0][1]['content'][0]
    information_systems = structure['column-8'][0][1]['content'][0]

    home_slider_portlet = structure['column-1']
    home_search_portlet = structure['column-2']
    news_portlet = structure['column-5']
    events_portlet = structure['column-6']

    return noop(country_selector, share_info, sector_policies,
                information_systems)


def run_importer(site=None):
    sql.Address = sql.Addres    # wrong detected plural
    for kname, rels in RELATIONS.items():
        logger.info("Setting relations for %s", kname)
        klass = getattr(sql, kname)
        for name, info in rels.items():
            other = getattr(sql, info['other'])
            pj = "and_(%s.%s==%s.%s)" % (info['other'], info['fk'], kname,
                                         info['fk'])
            rel = relationship(other,
                               foreign_keys=getattr(klass, info['fk']),
                               backref=info['bref'],
                               primaryjoin=pj,
                               )
            setattr(klass, name, rel)

    if 'dbshell' in sys.argv:
        import pdb; pdb.set_trace()

    if site is None:
        site = get_plone_site()

    structure = ['content', 'aceprojects', 'casestudy', 'adaptationoption',
                 'repository']
    for name in structure:
        if name not in site.contentIds():
            site.invokeFactory("Folder", name)

    for image in session.query(sql.Image):
        import_image(image, site['repository'])

    for layout in session.query(sql.Layout).filter_by(privatelayout=False):
        import_layout(layout, site)

    for dlfileentry in session.query(sql.Dlfileentry):
        import_dlfileentry(dlfileentry, site['repository'])

    for aceitem in session.query(sql.AceAceitem):
        import_aceitem(aceitem, site['content'])

    for aceproject in session.query(sql.AceProject):
        import_aceproject(aceproject, site['aceprojects'])

    for acemeasure in session.query(sql.AceMeasure):
        if acemeasure.mao_type == 'A':
            import_casestudy(acemeasure, site['casestudy'])
        else:
            import_adaptationoption(acemeasure, site['adaptationoption'])


def get_plone_site():
    import Zope2
    app = Zope2.app()
    from Testing.ZopeTestCase.utils import makerequest
    app = makerequest(app)
    app.REQUEST['PARENTS'] = [app]
    from zope.globalrequest import setRequest
    setRequest(app.REQUEST)
    from AccessControl.SpecialUsers import system as user
    from AccessControl.SecurityManagement import newSecurityManager
    newSecurityManager(None, user)

    _site = app['Plone']
    site = _site.__of__(app)

    from zope.site.hooks import setSite
    setSite(site)

    return site


def main():
    """ Run the ClimateAdapt import process

    This should be run through the zope client script running machinery, like so:

    DB=postgres://postgres:pwd@localhost/climate bin/www1 run bin/climateadapt_importer
    """
    global session
    engine = create_engine(os.environ.get("DB"))
    Session = scoped_session(sessionmaker(bind=engine))
    register(Session, keep_session=True)
    session = Session()
    run_importer()
    transaction.commit()

    return


def import_handler(context):
    """ A GenericSetup import handler.

    Use it like above, start the Zope process with the DB parameter on command line
    """
    global session
    engine = create_engine(os.environ.get("DB"))
    Session = scoped_session(sessionmaker(bind=engine))
    register(Session, keep_session=True)
    session = Session()

    site = context.getSite()
    run_importer(site)
