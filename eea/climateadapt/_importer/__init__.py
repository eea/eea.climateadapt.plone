from collections import defaultdict
from eea.climateadapt._importer import sqlschema as sql
from eea.climateadapt._importer.tweak_sql import fix_relations
from eea.climateadapt._importer.utils import ACE_ITEM_TYPES
from eea.climateadapt._importer.utils import create_cover_at
from eea.climateadapt._importer.utils import extract_portlet_info
from eea.climateadapt._importer.utils import get_image_by_imageid
from eea.climateadapt._importer.utils import localize
from eea.climateadapt._importer.utils import log_call
from eea.climateadapt._importer.utils import logger
from eea.climateadapt._importer.utils import make_aceitem_search_tile
from eea.climateadapt._importer.utils import make_ast_navigation_tile
from eea.climateadapt._importer.utils import make_countries_dropdown_tile
from eea.climateadapt._importer.utils import make_group
from eea.climateadapt._importer.utils import make_iframe_embed_tile
from eea.climateadapt._importer.utils import make_image_tile
from eea.climateadapt._importer.utils import make_layout
from eea.climateadapt._importer.utils import make_richtext_tile
from eea.climateadapt._importer.utils import make_richtext_with_title_tile
from eea.climateadapt._importer.utils import make_row
from eea.climateadapt._importer.utils import make_share_tile
from eea.climateadapt._importer.utils import make_text_from_articlejournal
from eea.climateadapt._importer.utils import make_tile
from eea.climateadapt._importer.utils import make_transregion_dropdown_tile
from eea.climateadapt._importer.utils import noop
from eea.climateadapt._importer.utils import pack_to_table
from eea.climateadapt._importer.utils import parse_settings, s2l    #, printe
from eea.climateadapt._importer.utils import render
from eea.climateadapt._importer.utils import render_accordion
from eea.climateadapt._importer.utils import render_tabs
from eea.climateadapt._importer.utils import strip_xml
from eea.climateadapt.interfaces import IASTNavigationRoot
from eea.climateadapt.interfaces import IBalticRegionMarker
from eea.climateadapt.interfaces import ITransnationalRegionMarker
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.interface import alsoProvides
from zope.sqlalchemy import register
import json
import os
import sys
import transaction


session = None      # this will be a global bound to the current module

MAPOFLAYOUTS = defaultdict(list)


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
            data_type=data.datatype,
            storage_type=data.storagetype,
            sectors=s2l(data.sectors_),
            elements=s2l(data.elements_),
            climate_impacts=s2l(data.climateimpacts_),
            source=data.source,
            comments=data.comments,
            year=int(data.year or '0'),
            geochars=data.geochars,
            special_tags=s2l(data.specialtagging),
            rating=data.rating,
        )
        item._aceitem_id = data.aceitemid

        logger.info("Imported aceitem %s from sql aceitem %s",
                    item, data.aceitemid)
        item.reindexObject()
        return item
    else:
        import pdb; pdb.set_trace()
        raise ValueError("You missed an acetype item: %s" % data.datatype)


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
        rating=data.rating,
    )

    item._aceproject_id = data.projectid
    item.reindexObject()

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
        rating=data.rating,
    )
    item._acemeasure_id = data.measureid
    item.reindexObject()

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
        description=data.description,
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
        rating=data.rating,
    )

    item._acemeasure_id = data.measureid
    item.reindexObject()

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

    item.reindexObject()
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

    item._uuid = data.uuid_

    logger.info("Imported %s from sql dlentry %s", item, data.fileentryid)

    item.reindexObject()

    return item


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

WATCH = [
#   '/observations-and-scenarios',
#   u'/transnational-regions/baltic-sea/policy-framework'
]


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

    if layout.friendlyurl in WATCH:
        import pdb; pdb.set_trace()

    settings = parse_settings(layout.typesettings)

    if layout.type_ == u'link_to_layout':
        # TODO: this is a shortcut link should create as a folder and add the linked layout as default page
        #linked_layoutid = settings['linkToLayoutId']
        return

    template = settings['layout-template-id'][0]
    MAPOFLAYOUTS[template].append(layout.friendlyurl)
    #print layout.type_, "\t\t", template, "\t\t", layout.friendlyurl

    logger.info("Importing layout %s at url %s with template %s",
                layout.layoutid, layout.friendlyurl, template)

    is_column = lambda s: (s.startswith('column-')
                           and not s.endswith('-customizable'))

    structure = {}

    structure['name'] = strip_xml(layout.name)

    for column, portlet_ids in filter(lambda kv: is_column(kv[0]),
                                      settings.items()):
        structure[column] = []   # a column is a list of portlets
        for portletid in portlet_ids:
            content = extract_portlet_info(session, portletid, layout)
            structure[column].append((portletid, content))

    importer = globals().get('import_template_' + template)
    cover = importer(site, layout, structure)
    if cover is not None:
        cover.reindexObject()
    return cover


# possible templates are
# 1_2_1_columns         - done
# 1_2_columns_i         - TODO as custom page
# 1_2_columns_ii        - done
# 1_column              - done
# 2_columns_i           - done
# 2_columns_ii          - these need to be manually created
# 2_columns_iii         - done
# ace_layout_1          - is not needed?
# ace_layout_2          - done
# ace_layout_3          - done
# ace_layout_4          - done
# ace_layout_5          - done
# ace_layout_col_1_2    - done
# ast                   - done using urban_ast
# faq                   - done
# frontpage             - TODO as a custom page
# transnationalregion   - done
# urban_ast             - done with TODOs


@log_call
def import_template_1_2_1_columns(site, layout, structure):
    # DONE

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
    cover._p_changed = True
    cover._layout_id = layout.layoutid

    # layout = [{'type': 'row', 'children': []}]

    nav_tile = make_richtext_tile(cover, {'title': 'navigation', 'text': nav})
    text_tile = make_richtext_tile(cover, {'title': 'text', 'text': text})
    iframe_tile = make_iframe_embed_tile(cover, iframe)

    # we create 3 rows, each with a separate tile

    layout = make_layout(*[make_row(make_group(tile))
                          for tile in (nav_tile, text_tile, iframe_tile) ])

    layout = json.dumps(layout)

    cover.cover_layout = layout
    return cover


@log_call
def import_template_transnationalregion(site, layout, structure):
    # DONE

    # a country page is a structure with 3 "columns":
    # column-1 has an image and a select box to select other countries
    # column-2 has is a structure of tabs and tables
    # column-3 is unknown and will be ignored
    # Ex: /countries/liechtenstein

    # TODO: "translate" the titles for tabs and table header
    # TODO: add the countries select dropdown

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

    main_content = render_tabs(payload)

    cover = create_cover_at(site, layout.friendlyurl)
    cover._p_changed = True
    cover._layout_id = layout.layoutid

    image_tile = make_image_tile(site, cover, image_info)    # TODO: import image
    content_tile = make_richtext_tile(cover, {'title': 'main content',
                                              'text': main_content})

    image_group = make_group(2, image_tile)
    content_group = make_group(14, content_tile)

    layout = make_layout(make_row(image_group, content_group))
    cover.cover_layout = json.dumps(layout)
    cover._p_changed = True
    return cover


@log_call
def import_template_ace_layout_2(site, layout, structure):
    # Done

    # TODO: relevant tiles, search tiles, relevent with filtering

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

    name = structure['name']
    cover = create_cover_at(site, layout.friendlyurl, title=str(name))
    cover._layout_id = layout.layoutid

    main = {}

    title = structure['column-1'][0][1]['content'][1][2][0]
    body = structure['column-1'][0][1]['content'][2][2][0]
    readmore = structure['column-1'][0][1]['content'][3][2][0]
    image_id = structure['column-1'][0][1]['content'][0][2][0]
    image = get_image_by_imageid(site, image_id)

    main['title'] = title
    main['body'] = body
    main['readmore'] = readmore
    main['image'] = {
        'title': image.Title(),
        'thumb': localize(image.absolute_url(1)) + "/@@images/image",
    }
    main_content = render('templates/richtext_readmore_and_image.pt',
                          {'payload': main})

    main_content_tile = make_richtext_tile(cover, {'title': 'main content',
                                                   'text': main_content})

    col2_tile = make_tile(cover, structure['column-2'])
    col3_tile = make_tile(cover, structure['column-3'])

    relevant_content_tiles = [col2_tile, col3_tile]
    sidebar_tile = make_tile(cover, structure['column-4'])
    sidebar_group = make_group(2, sidebar_tile)
    main_content_group = make_group(14,
                                    main_content_tile, *relevant_content_tiles)
    layout = make_layout(make_row(main_content_group, sidebar_group))
    layout = json.dumps(layout)

    cover.cover_layout = layout
    return cover


@log_call
def import_template_ace_layout_col_1_2(site, layout, structure):
    # done

    # TODO: fix the iframe, it's too small

    # this is a 2 column page with some navigation on the left and a big
    # iframe (or just plain html text) on the right
    # example page: http://adapt-test.eea.europa.eu//tools/urban-adaptation/climatic-threats/heat-waves/sensitivity
    assert(len(structure) == 3)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-3']) == 1)

    title = strip_xml(structure['name'])
    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover._layout_id = layout.layoutid

    main = structure['column-3'][0][1].get('url')
    if not main:
        main = structure['column-3'][0][1]['content'][0]
        info = {
            'title': title,
            'text': main,
        }
        main_tile = make_richtext_tile(cover, info)
    else:
        main_tile = make_iframe_embed_tile(cover, main)

    nav_menu = structure['column-1'][0][1]['content'][0]    # TODO: fix nav menu links
    info = {
        'title': 'navigation',
        'text': nav_menu
    }
    nav_tile = make_richtext_tile(cover, info)

    nav_group = make_group(1, nav_tile)
    main_group = make_group(15, main_tile)

    layout = make_layout(make_row(nav_group, main_group))
    layout = json.dumps(layout)

    cover.cover_layout = layout

    return cover


@log_call
def import_template_ace_layout_3(site, layout, structure):
    # this is a "details" page, ex: http://adapt-test.eea.europa.eu/transnational-regions/baltic-sea/policy-framework
    # main column has an image, title, main text and "read more text"
    # sidebar has a aceitem search portlet
    # extra, there is an id for a tab based navigation, as a separate column
    # called 'name'
    # some pages may contain extra columns under the main column

    main = {}
    col1 = structure.pop('column-1')
    for line in col1[0][1]['content']:
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

    name = structure.pop('name')
    sidebar = structure.pop('column-5')

    extra_columns = [structure[k] for k in sorted(structure.keys())]

    cover = create_cover_at(site, layout.friendlyurl, title=name)
    cover._p_changed = True
    cover._layout_id = layout.layoutid

    if layout.themeid == "balticseaace_WAR_acetheme":
        # TODO: mark the content with a special interface to enable the menu
        alsoProvides(cover, IBalticRegionMarker)

    image = get_image_by_imageid(site, main['image'])
    main['image'] = {
        'title': image.Title(),
        'thumb': localize(image.absolute_url(1)) + "/@@images/image",
    }
    main_content = render('templates/richtext_readmore_and_image.pt',
                          {'payload': main})

    main_content_tile = make_richtext_tile(cover, {'title': 'main content',
                                                   'text': main_content})
    relevant_content_tiles = [
        make_tile(cover, col) for col in extra_columns
    ]

    sidebar_tile = make_aceitem_search_tile(cover, sidebar[0][1])
    sidebar_group = make_group(2, sidebar_tile)
    main_content_group = make_group(14,
                                    main_content_tile, *relevant_content_tiles)
    layout = make_layout(make_row(main_content_group, sidebar_group))
    cover.cover_layout = json.dumps(layout)
    cover._p_changed = True

    return cover


@log_call
def import_template_ace_layout_4(site, layout, structure):
    # done

    # TODO: the facts is not saved properly? shows labels instead of values

    # these are Project pages such as http://adapt-test.eea.europa.eu/web/guest/project/climsave

    title = structure['name']
    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover._p_changed = True
    cover._layout_id = layout.layoutid

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
    sidebar_title = structure['column-2'][0][1]['portlet_title']
    sidebar = []
    _contact = []
    for line in _main_sidebar:
        if line[1] != 'Contact':
            sidebar.append((line[1], line[2][0]))
        else:
            #contact = []
            for subline in line[2]:
                if not subline:
                    continue
                _contact.append((subline[1], subline[2][0]))
            #sidebar.append(contact)

    contact_text = render("templates/snippet_contact.pt", {'lines': _contact})
    sidebar_text = render("templates/snippet_sidebar_text.pt",
                          {'lines': sidebar})
    sidebar_tile = make_richtext_with_title_tile(cover,
                                      {'title': sidebar_title,
                                       'text': sidebar_text + contact_text})

    sidebar_tiles = [sidebar_tile]

    if len(structure['column-2']) > 1:
        for pid, portlet in structure['column-2'][1:]:
            tile = make_richtext_with_title_tile(
                cover, {'title': portlet['portlet_title'],
                        'text': portlet['content'][0]})
            sidebar_tiles.append(tile)

    # the accordion is a list of ('tab title', 'tab content structure')
    # we need to go through each of the tabs and change the structure to be html

    # TODO: fix accordion, it's not rendered properly (all tabs closed, etc)
    payload = []
    for k, v in main['accordion']:
        # TODO: get the keys from dictionary
        if not k == 'ProjectPartners':
            payload.append((k, v))
        else:
            table = {'rows': v, 'cols': []}
            payload.append((k, render('templates/table.pt', table)))

    image = get_image_by_imageid(site, main['image'])
    accordion = render_accordion(payload)
    main_text = render('templates/project.pt',
                       {'image': localize(image.absolute_url(1)) + "/@@images/image",
                        'title': main['title'],
                        'subtitle': main['subtitle'],
                        'accordion': accordion
                        })

    main_tile = make_richtext_tile(cover, {'title': 'main content',
                                           'text': main_text})
    sidebar_group = make_group(2, *sidebar_tiles)
    main_content_group = make_group(10, main_tile)

    layout = make_layout(make_row(main_content_group, sidebar_group))

    cover.cover_layout = json.dumps(layout)
    cover._p_changed = True

    return cover


@log_call
def import_template_ast(site, layout, structure):
    # done
    # TODO: AST navigation menu
    # TODO: portlets order is not preserved?

    # column-1 has the imagemap on the left side
    # column-2 has 2 portlets:  title and then the one with content (which also
    # has a title)

    assert(len(structure) >= 3)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-2']) >= 2)

    return import_template_urban_ast(site, layout, structure)

    # image_portlet = structure['column-1'][0][1]['content'][0]
    # header_text = structure['column-2'][0][1]['headertext']
    # content = structure['column-2'][1][1]['content'][0]
    #
    # content_portlet = None
    # if len(structure['column-2']) > 2:
    #     assert(len(structure['column-2']) == 3)
    #     content_portlet = structure['column-2'][2]
    #
    # extra_columns = {}
    # [structure.pop(x) for x in ('name', 'column-1', 'column-2')]
    # for key in structure:
    #     portlet_name = structure[key][0][1]['portletSetupTitle_en_GB']
    #     extra_columns[portlet_name] = structure[key]
    #
    # noop(image_portlet, header_text, content, content_portlet, extra_columns)
    #

@log_call
def import_template_urban_ast(site, layout, structure):
    # TODO: fix images
    # TODO: fix urban ast navigation
    # TODO: create nav menu on the left
    # TODO: use the step information
    # TODO: cleanup the css in image_portlet


    # column-1 has the imagemap on the left side
    # column-2 has 2 portlets:  title and then the one with content (which also
    # has a title)
    # there can be more columns where there are tiles with search

    assert(len(structure) >= 3)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-2']) >= 2)

    name = structure['name']
    image_portlet = structure['column-1'][0][1]['content'][0]
    header_text = structure['column-2'][0][1]['headertext']
    # step = structure['column-2'][0][1]['step']
    portlet = structure['column-2'][1][1]
    subtitle = portlet['portlet_title']

    main_text = make_text_from_articlejournal(portlet['content'])

    payload = {
        'title': header_text,
        'subtitle': subtitle,
        'main_text': main_text
    }
    main_content = render('templates/ast_text.pt', payload)

    cover = create_cover_at(site, layout.friendlyurl, title=unicode(name))
    cover._p_changed = True
    cover._layout_id = layout.layoutid

    image_tile = make_richtext_tile(cover, {'text': image_portlet,
                                            'title': 'AST Image'})
    main_content_tile = make_richtext_tile(cover, {'text': main_content,
                                                   'title': 'Main text'})
    # nav_tile = make_richtext_tile(cover, {'text': 'nav here', 'title': 'nav'})
    nav_tile = make_ast_navigation_tile(cover)

    side_group = make_group(2, image_tile, nav_tile)

    step = structure['column-2'][0][1]['step']

#  u'column-2': [(u'astheaderportlet_WAR_ASTHeaderportlet_INSTANCE_AQlGpTEbY3Eg',
#                 {'headertext': u'Implementation',
#                  'portletSetupCss': u'{"wapData":{"title":"","initialWindowState":"NORMAL"},"spacingData":{"margin":{"sameForAll":true,"bottom":{"unit":"px","value":""},"left":{"unit":"px","value":""},"right":{"unit":"px","value":""},"top":{"unit":"px","value":""}},"padding":{"sameForAll":true,"bottom":{"unit":"px","value":""},"left":{"unit":"px","value":""},"right":{"unit":"px","value":""},"top":{"unit":"px","value":""}}},"borderData":{"borderStyle":{"sameForAll":true,"bottom":"","left":"","right":"","top":""},"borderColor":{"sameForAll":true,"bottom":"","left":"","right":"","top":""},"borderWidth":{"sameForAll":true,"bottom":{"unit":"px","value":""},"left":{"unit":"px","value":""},"right":{"unit":"px","value":""},"top":{"unit":"px","value":""}}},"textData":{"fontWeight":"","lineHeight":"","textDecoration":"","letterSpacing":"","color":"","textAlign":"","fontStyle":"","fontFamily":"","wordSpacing":"","fontSize":""},"bgData":{"backgroundPosition":{"left":{"unit":"px","value":""},"top":{"unit":"px","value":""}},"backgroundColor":"","backgroundRepeat":"","backgroundImage":"","useBgImage":false},"advancedData":{"customCSS":"","customCSSClassName":""}}',
#                  'portletSetupShowBorders': u'false',
#                  'portletSetupUseCustomTitle': u'false',
#                  'step': u'5'}),


    [structure.pop(z) for z in ['column-1', 'column-2', 'name']]
    if structure:
        second_row_group = [make_group(4, t) for t in
                            [make_tile(cover, x) for x in structure.values()]
                            ]
        second_row = make_row(*second_row_group)
        main_group = make_group(14, main_content_tile, second_row)
    else:
        main_group = make_group(14, main_content_tile)

    layout = make_layout(make_row(side_group, main_group))
    cover.cover_layout = json.dumps(layout)
    cover._ast_navigation_step = int(step)

    return cover


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
    # done

    # ex page: /share-your-info/general

    # TODO: column02 contains sharemeasureportlet
    # TODO: mark the cover with an interface to show a viewlet with navigation
    # TODO: doesn't show title? Cover should be able to show its title
    # TODO: fix for above is to set layout to standard in display menu

    # row 1: text + image
    # row 2: share button

    assert(len(structure) == 2 or len(structure) == 3)
    assert(len(structure['column-1']) == 1)
    if len(structure) > 2:
        assert(len(structure['column-2']) == 1)

    image = structure['column-1'][0][1]['content'][0][2][0]
    title = structure['column-1'][0][1]['content'][1][2][0]
    body = structure['column-1'][0][1]['content'][2][2][0]

    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover._p_changed = True
    cover._layout_id = layout.layoutid

    share_portlet = None
    share_portlet_title = ""
    if len(structure) == 3:
        share_portlet = structure['column-2'][0][1]
        share_portlet_title = structure['column-2'][0][0]

    info = {'title': title, 'text': body}
    main_text_tile = make_richtext_tile(cover, info)
    image_tile = make_image_tile(site, cover, {'id': image})

    if share_portlet:
        sharetype = share_portlet.get('sharetype')
        if not sharetype:
            if 'shareprojectportlet' in share_portlet_title:
                sharetype = 'RESEARCHPROJECT'
            elif share_portlet.get('caseStudiesFeatureType'):
                sharetype = 'ACTION'
            else:
                sharetype = 'MEASURE'
        share_tile = make_share_tile(cover, sharetype)

    main_text_group = make_group(12, main_text_tile)
    image_group = make_group(4, image_tile)
    row_1 = make_row(main_text_group, image_group)

    if share_portlet:
        row_2 = make_row(make_group(16, share_tile))
        layout = make_layout(row_1, row_2)
    else:
        layout = make_layout(row_1)

    cover.cover_layout = json.dumps(layout)

    return cover


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

    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover._p_changed = True
    cover._layout_id = layout.layoutid

    if len(structure['column-1']) > 2:
        col1 = u"".join(content)
        col2 = u"".join(structure['column-1'][1][1]['content'][0])

        col1_tile = make_richtext_tile(cover, {'title': 'col1', 'text': col1})
        col2_tile = make_richtext_tile(cover, {'title': 'col1', 'text': col2})
        iframe = structure['column-1'][2][1]['url']
        iframe_tile = make_iframe_embed_tile(cover, iframe)

        col1_group = make_group(8, col1_tile)
        col2_group = make_group(8, col2_tile)
        iframe_group = make_group(16, iframe_tile)

        row_1 = make_row(col1_group, col2_group)
        row_2 = make_row(iframe_group)
        layout = make_layout(row_1, row_2)

    else:
        if isinstance(content[0], tuple):
            # this is a dynamic portlet
            logger.warning("Please investigate this importer %s with template %s",
                        layout.friendlyurl, '1_column')
            return

        main_text_tile = make_richtext_with_title_tile(cover,
                                                    {'title': portlet_title,
                                                    'text': u"".join(content)})

        main_group = make_group(16, main_text_tile)
        layout = make_layout(make_row(main_group))

    cover.cover_layout = json.dumps(layout)
    cover._p_changed = True
    return cover


@log_call
def import_template_2_columns_i(site, layout, structure):
    # done

    # ex: /countries
    # TODO: fix images linking

    assert(len(structure) in [2, 3])

    title = structure['name']

    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover._p_changed = True
    cover._layout_id = layout.layoutid

    if len(structure) == 3:
        countries_portlet = structure['column-1'][0][1]
        body = structure['column-2'][0][1]['content'][0]
        portlet_title = structure['column-2'][0][1]['portlet_title']
    else:
        countries_portlet = None
        body = structure['column-1'][0][1]['content'][0]
        portlet_title = structure['column-1'][0][1]['portlet_title']

    main_text_tile = make_richtext_with_title_tile(cover,
                                                   {'title': portlet_title,
                                                    'text': body})
    if countries_portlet:
        countries_tile = make_countries_dropdown_tile(cover)
        main_group = make_group(16, main_text_tile, countries_tile)
    else:
        main_group = make_group(16, main_text_tile)

    layout = make_layout(make_row(main_group))
    cover.cover_layout = json.dumps(layout)
    cover._p_changed = True
    return cover


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
    # done

    # ex: /organisations
    assert(len(structure) == 2 or len(structure) == 3)

    #title = structure['name']
    title = structure['column-1'][0][1]['portlet_title']
    body = structure['column-1'][0][1]['content'][0]

    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover._p_changed = True
    cover._layout_id = layout.layoutid

    extra_tiles = []
    if len(structure['column-1']) == 4:
        # There is only one layout with this structure
        # TODO: do this page, it's the /organisations page
        # filter_portlet_1 = structure['column-1'][1]
        # filter_portlet_2 = structure['column-1'][2]
        # blue_button = structure['column-1'][3][1]['content'][0]
        extra_tiles = [make_tile(cover, [p]) for p in structure['column-1'][1:]]
    elif len(structure['column-1']) == 2:
        body += structure['column-1'][1][1]['content'][0]

    image = None
    if len(structure) == 3:
        # column-2 has a image
        assert(len(structure['column-2']) == 1)
        image = structure['column-2'][0][1]['content'][0]

    title = structure['name']

    main_content_tile = make_richtext_tile(cover, {'text': body,
                                                   'title': 'Main text'})
    if image:
        image_tile = make_richtext_tile(cover, {'text': image,
                                                'title': 'image'})
        side_group = make_group(2, image_tile)
        main_group = make_group(10, main_content_tile, *extra_tiles)
        layout = make_layout(make_row(main_group, side_group))
    else:
        main_group = make_group(16, main_content_tile)
        layout = make_layout(make_row(main_group))

    cover.cover_layout = json.dumps(layout)
    return cover


@log_call
def import_template_ace_layout_1(site, layout, structure):
    # ex page: /home (may be just a mockup for home page)
    logger.warning("Please investigate this importer %s with template %s",
                   layout.friendlyurl, 'ace_layout_1')


@log_call
def import_template_ace_layout_5(site, layout, structure):
    # done
    # TODO: fix the dropdown select template, needs JS work
    # ex page: /transnational-regions/caribbean-area
    # 1 row, 2 columns. First column: image + region selection tile
    #                   Second column: rich text

    assert(len(structure) == 4)
    assert(len(structure['column-1']) == 1)

    title = structure['name']
    image = structure['column-1'][0][1]['content'][0][2][0]
    _first = structure['column-2'][0][1]['content'][0][2][0]

    if len(structure['column-2'][0][1]['content']) == 2:
        _second = structure['column-2'][0][1]['content'][1][2][0]
        _first += _second

    # tr_portlet = structure['column-3']
    cover = create_cover_at(site, layout.friendlyurl, title=title)
    alsoProvides(cover, ITransnationalRegionMarker)

    info = {'title': title, 'text': _first }
    main_text_tile = make_richtext_tile(cover, info)

    main_text_group = make_group(14, main_text_tile)
    dropdown_tile = make_transregion_dropdown_tile(cover)
    image_info = {
        'id': image,
        'description': '',
        'title': 'region image',
    }
    image_tile = make_image_tile(site, cover, image_info)    # TODO: import image
    image_group = make_group(2, image_tile, dropdown_tile)
    row_1 = make_row(image_group, main_text_group)

    layout = make_layout(row_1)

    cover.cover_layout = json.dumps(layout)

    return cover


@log_call
def import_template_faq(site, layout, structure):
    """ This is a template with a main body text and three columns of HTML
    underneath.
    Ex:/uncertainty-guidance-ai
    """

    # done
    # TODO: fix styling of columns
    # TODO: fix images path

    assert(len(structure) == 5)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-2']) == 1)
    assert(len(structure['column-3']) == 1)
    assert(len(structure['column-4']) == 1)

    main_text = structure['column-1'][0][1]['content'][0]
    col1 = structure['column-2'][0][1]['content'][0]
    col2 = structure['column-3'][0][1]['content'][0]
    col3 = structure['column-4'][0][1]['content'][0]

    title = structure['name']

    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover._p_changed = True
    cover._layout_id = layout.layoutid

    info = {'title': title, 'text': main_text}
    main_text_tile = make_richtext_tile(cover, info)
    main_text_group = make_group(16, main_text_tile)

    col_tiles = [
        make_richtext_tile(cover, {'text': col, 'title': 'column'})
        for col in [col1, col2, col3]
    ]
    row_1 = make_row(main_text_group)
    row_2 = make_row(make_group(4, *col_tiles))
    layout = make_layout(row_1, row_2)

    cover.cover_layout = json.dumps(layout)

    return cover


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

    # home_slider_portlet = structure['column-1']
    # home_search_portlet = structure['column-2']
    # news_portlet = structure['column-5']
    # events_portlet = structure['column-6']

    return noop(country_selector,
                share_info,
                sector_policies,
                information_systems)


def run_importer(site=None):
    sql.Address = sql.Addres    # wrong detected plural
    fix_relations(session)

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

    for dlfileentry in session.query(sql.Dlfileentry):
        import_dlfileentry(dlfileentry, site['repository'])

    for aceitem in session.query(sql.AceAceitem):
        if aceitem.datatype in ['ACTION', 'MEASURE']:
            # TODO: log and solve here
            continue
        import_aceitem(aceitem, site['content'])

    for aceproject in session.query(sql.AceProject):
        import_aceproject(aceproject, site['aceprojects'])

    for acemeasure in session.query(sql.AceMeasure):
        if acemeasure.mao_type == 'A':
            import_casestudy(acemeasure, site['casestudy'])
        else:
            import_adaptationoption(acemeasure, site['adaptationoption'])

    for layout in session.query(sql.Layout).filter_by(privatelayout=False):
        cover = import_layout(layout, site)
        if cover:
            cover._imported_comment = \
                "Imported from layout {0}".format(layout.layoutid)
            logger.info("Created cover at %s", cover.absolute_url())

    ast_tools = ['tools/urban-ast',
                 'adaptation-support-tool']
    # for path in ast_tools:
    #     obj = site.restrictedTraverse(ast_tools)
    #     if not IASTNavigationRoot.providedBy(obj):
    #         alsoProvides(obj, IASTNavigationRoot)


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
    if context.readDataFile('eea.climateadapt.importer.txt') is None:
        return
    global session
    engine = create_engine(os.environ.get("DB"))
    Session = scoped_session(sessionmaker(bind=engine))
    register(Session, keep_session=True)
    session = Session()

    site = context.getSite()
    run_importer(site)
