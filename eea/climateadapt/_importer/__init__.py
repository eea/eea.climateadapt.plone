from datetime import datetime as dt
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from collections import defaultdict
from eea.climateadapt._importer import sqlschema as sql
from eea.climateadapt._importer.tweak_sql import fix_relations
from eea.climateadapt._importer.utils import ACE_ITEM_TYPES
from eea.climateadapt._importer.utils import _get_latest_version
from eea.climateadapt._importer.utils import createAndPublishContentInContainer
from eea.climateadapt._importer.utils import create_cover_at
from eea.climateadapt._importer.utils import create_folder_at
from eea.climateadapt._importer.utils import create_plone_content
from eea.climateadapt._importer.utils import extract_portlet_info
from eea.climateadapt._importer.utils import extract_simplified_info_from_article_content
from eea.climateadapt._importer.utils import get_image_by_imageid
from eea.climateadapt._importer.utils import localize
from eea.climateadapt._importer.utils import log_call
from eea.climateadapt._importer.utils import logger
from eea.climateadapt._importer.utils import make_aceitem_search_tile
from eea.climateadapt._importer.utils import make_ast_navigation_tile
from eea.climateadapt._importer.utils import make_countries_dropdown_tile
from eea.climateadapt._importer.utils import make_faceted
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
from eea.climateadapt._importer.utils import make_urbanast_navigation_tile
from eea.climateadapt._importer.utils import make_urbanmenu_title
from eea.climateadapt._importer.utils import make_view_tile
# from eea.climateadapt._importer.utils import noop
from eea.climateadapt._importer.utils import pack_to_table
from eea.climateadapt._importer.utils import parse_settings, s2l    #, printe
from eea.climateadapt._importer.utils import render
from eea.climateadapt._importer.utils import render_accordion
from eea.climateadapt._importer.utils import render_tabs
from eea.climateadapt._importer.utils import s2li
from eea.climateadapt._importer.utils import stamp_cover
from eea.climateadapt._importer.utils import strip_xml
from eea.climateadapt._importer.utils import t2r
from eea.climateadapt._importer.utils import to_decimal
from eea.climateadapt.interfaces import IASTNavigationRoot
from eea.climateadapt.interfaces import IBalticRegionMarker
from eea.climateadapt.interfaces import IClimateAdaptSharePage
from eea.climateadapt.interfaces import ISiteSearchFacetedView
from eea.climateadapt.interfaces import ITransnationalRegionMarker
from eea.climateadapt.vocabulary import _cca_types
from eea.climateadapt.vocabulary import ace_countries_dict
from eea.climateadapt.vocabulary import _stage_implementation_cycle
from eea.climateadapt.vocabulary import _status_of_adapt_signature
from eea.climateadapt.vocabulary import aceitem_climateimpacts_vocabulary
from eea.climateadapt.vocabulary import _already_devel_adapt_strategy
from eea.climateadapt.vocabulary import key_vulnerable_adapt_sector_vocabulary
from eea.climateadapt.vocabulary import aceitem_elements_vocabulary
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from pytz import utc
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from subprocess import check_output
from z3c.relationfield.relation import RelationValue
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides, noLongerProvides
from zope.intid.interfaces import IIntIds
from zope.sqlalchemy import register
import dateutil
import json
import os
import pprint
import re
import sys
import transaction


session = None      # this will be a global bound to the current module

MAPOFLAYOUTS = defaultdict(list)

additional_sharepage_layouts = [
    '/share-your-info/indicators',
    '/share-your-info/map-graph-data'
]


@log_call
def import_aceitem(data, location):
    # TODO: Some AceItems have ACTION, MEASURE, REASEARCHPROJECT types and
    # should be mapped over AceMeasure and AceProject

    if data.datatype in ACE_ITEM_TYPES:
        item = createAndPublishContentInContainer(
            location,
            ACE_ITEM_TYPES[data.datatype],
            title=data.name,
            long_description=t2r(data.description),
            keywords=data.keyword,
            spatial_layer=data.spatiallayer,
            spatial_values=s2l(data.spatialvalues),
            data_type=data.datatype,
            storage_type=data.storagetype,
            sectors=s2l(data.sectors_),
            elements=s2l(data.elements_),
            climate_impacts=s2l(data.climateimpacts_),
            websites=s2l(data.storedat),
            source=t2r(data.source),
            comments=data.comments,
            year=int(data.year or '0'),
            geochars=data.geochars,
            special_tags=s2l(data.specialtagging, relaxed=True),
            rating=data.rating,
        )
        item._aceitem_id = data.aceitemid

        logger.info("Imported aceitem %s from sql aceitem %s",
                    item.absolute_url(1), data.aceitemid)
        item.reindexObject()
        return item
    else:
        import pdb; pdb.set_trace()
        raise ValueError("You missed an acetype item: %s" % data.datatype)


@log_call
def import_aceproject(data, location):
    item = createAndPublishContentInContainer(
        location,
        'eea.climateadapt.aceproject',
        title=data.title,
        #long_description=t2r(data.description),    # doesn't have description
        acronym=data.acronym,
        lead=data.lead,
        website=data.website,
        abstracts=t2r(data.abstracts),
        source=t2r(data.source),
        partners=t2r(data.partners),
        keywords=t2r(data.keywords),
        sectors=s2l(data.sectors),
        elements=s2l(data.element),
        climate_impacts=s2l(data.climateimpacts),
        funding=data.funding,
        duration=data.duration,
        specialtagging=data.specialtagging,
        geochars=data.geochars,
        spatial_layer=s2l(data.spatiallayer),
        spatial_values=s2l(data.spatialvalues),
        comments=data.comments,
        rating=data.rating,
    )

    item._aceproject_id = data.projectid
    item.reindexObject()

    logger.info("Imported aceproject %s from sql aceproject %s",
                item.absolute_url(1), data.projectid)

    return item


@log_call
def import_adaptationoption(data, location):
    item = createAndPublishContentInContainer(
        location,
        'eea.climateadapt.adaptationoption',
        adaptationoptions=s2li(data.adaptationoptions),
        challenges=t2r(data.challenges),
        climate_impacts=s2l(data.climateimpacts_),
        comments=data.comments,
        contact=t2r(data.contact),
        cost_benefit=t2r(data.costbenefit),
        elements=s2l(data.elements_),
        geochars=data.geochars,
        implementation_time=t2r(data.implementationtime),
        implementation_type=data.implementationtype,
        #keywords=s2l(data.keywords, separators=[';', ',']),
        keywords=t2r(data.keywords),
        legal_aspects=t2r(data.legalaspects),
        lifetime=t2r(data.lifetime),
        long_description=t2r(data.description),
        measure_type=data.mao_type,
        objectives=t2r(data.objectives),
        rating=data.rating,
        relevance=s2l(data.relevance),
        sectors=s2l(data.sectors_),
        solutions=t2r(data.solutions),
        source=t2r(data.source),
        spatial_layer=data.spatiallayer,
        spatial_values=s2l(data.spatialvalues),
        stakeholder_participation=t2r(data.stakeholderparticipation),
        success_limitations=t2r(data.succeslimitations),
        title=data.name,
        websites=s2l(data.website),
    )
    item._acemeasure_id = data.measureid
    item.reindexObject()

    logger.info("Imported adaptation option %s from sql acemeasure %s",
                item.absolute_url(1), data.measureid)

    return item


@log_call
def import_casestudy(data, location):
    intids = getUtility(IIntIds)
    primephoto = None
    if data.primephoto:
        primephoto = get_image_by_imageid(location.aq_inner.aq_parent,
                                        data.primephoto)
    primephoto = primephoto and RelationValue(intids.getId(primephoto)) or None
    supphotos = []
    supphotos_str = data.supphotos is not None and data.supphotos or ''
    for supphotoid in supphotos_str.split(';'):
        supphoto = get_image_by_imageid(location.aq_inner.aq_parent,
                                        supphotoid)
        if supphoto:
            supphotos.append(RelationValue(intids.getId(supphoto)))
    item = createAndPublishContentInContainer(
        location,
        'eea.climateadapt.casestudy',
        adaptationoptions=s2li(data.adaptationoptions),
        challenges=t2r(data.challenges),
        climate_impacts=s2l(data.climateimpacts_),
        comments=data.comments,
        contact=t2r(data.contact),
        cost_benefit=t2r(data.costbenefit),
        elements=s2l(data.elements_),
        geochars=data.geochars,
        implementation_time=data.implementationtime,
        implementation_type=data.implementationtype,
        keywords=t2r(data.keywords),
        #keywords=s2l(data.keywords, separators=[',', ';']),
        legal_aspects=t2r(data.legalaspects),
        lifetime=data.lifetime,
        location_lat=to_decimal(data.lat),
        location_lon=to_decimal(data.lon),
        long_description=t2r(data.description),
        measure_type=data.mao_type,
        objectives=t2r(data.objectives),
        primephoto=primephoto,
        rating=data.rating,
        relevance=s2l(data.relevance),
        sectors=s2l(data.sectors_),
        solutions=t2r(data.solutions),
        source=data.source,
        spatial_layer=data.spatiallayer,
        spatial_values=s2l(data.spatialvalues),
        stakeholder_participation=t2r(data.stakeholderparticipation),
        success_limitations=t2r(data.succeslimitations),
        supphotos=supphotos,
        title=data.name,
        websites=s2l(data.website),
    )

    item._acemeasure_id = data.measureid
    item.reindexObject()

    logger.info("Imported casestudy %s from sql acemeasure %s",
                item.absolute_url(1), data.measureid)

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

    item = createAndPublishContentInContainer(
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
    logger.info("Imported image %s from sql Image %s",
                item.absolute_url(1), data.imageid)

    return item

@log_call
def import_dlfileversion(data, location):
    base_path = check_output([
        'find',
        './document_library',
        '-iname', '%s.%s' % (str(data.fileversionid),
                             data.extension)]).rstrip('\n')
    file_path = os.path.join(base_path, data.version)
    _r = "./document_library/%s/0/document_thumbnail/%s/[^/]*/[^/]*/%s/%s.%s/%s"
    regexp = _r % (data.companyid,
                   data.repositoryid,  # or groupid
                   data.fileentryid,
                   data.fileversionid,
                   data.extension,
                   data.version)
    if not (os.path.isfile(file_path) and re.match(regexp, file_path)):
        # there is no file and no match
        logger.info('DEBUG dlfileversion NO MATCH: ' + file_path)
        return
    logger.info('FOUND dlfileversion: ' + file_path)

    try:
        file_data = open(file_path).read()
    except Exception:
        logger.warning("Image with id %d does not exist in the supplied "
                       "document library", data.imageid)
        return None

    item = createAndPublishContentInContainer(
        location,
        'Image',
        #title='Image ' + str(data.fileversionid),
        title=data.title,
        description=data.description,
        id=str(data.fileversionid) + '.' + data.extension,
        image=NamedBlobImage(
            filename=str(data.fileversionid) + '.' + data.extension,
            data=file_data
        )
    )

    item._uuid = data.uuid_
    item.reindexObject()
    logger.info("Imported image %s from sql Image %s",
                item.absolute_url(1), data.fileversionid)

    return item


@log_call
def import_dlfileentry(data, location):
    # data.companyid / data.repositoryid / data.name / data.version

    # treepath can be something like this:

    # /8910770/11271386/'
    # /10402/
    # /0/

    tp = data.treepath[1:-1]
    components = tp.split('/')
    if len(components) == 2:
        # we'll get the folderid from the treepath
        # TODO: try by original algorithm
        #     folderid = data.folderid or data.groupid
        folderid = components[1]
        fpath = ('./document_library/{0}/{1}/{2}/{3}'.format(
            str(data.companyid),
            str(folderid),
            str(data.name),
            data.version
        ))
    elif data.treepath == u'/0/':
        fpath = ('./document_library/{0}/{1}/{2}/{3}'.format(
            str(data.companyid),
            str(data.repositoryid),
            str(data.name),
            data.version
        ))

    elif len(components) == 1:
        fpath = ('./document_library/{0}/{1}/{2}/{3}'.format(
            str(data.companyid),
            components[0],
            str(data.name),
            data.version
        ))

    if not os.path.exists(fpath):
        logger.error("File with id %d and title '%s' does not exist in the "
                       "supplied document library", data.fileentryid,
                       data.title)
        return None

    file_data = open(fpath).read()

    if 'jpg' in data.extension or 'png' in data.extension:
        item = createAndPublishContentInContainer(
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
        item = createAndPublishContentInContainer(
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

    logger.info("Imported %s from sql dlentry %s",
                item.absolute_url(1), data.fileentryid)

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
        llid = int(settings['linkToLayoutId'][0])
        ll = session.query(sql.Layout).filter_by(layoutid=llid).one()
        this_url = layout.friendlyurl
        child_url = ll.friendlyurl
        folder = create_folder_at(site, this_url)
        folder.setLayout(child_url.split('/')[-1])
        folder.title = strip_xml(ll.name)
        return folder

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


def import_city_profile(container, journal):
    vals = extract_simplified_info_from_article_content(journal.content)
    data = {}
    for _type, name, payload in vals:
        if name is None:
            name = 'image'
        if payload:
            data[name] = payload[0]
        else:
            data[name] = None

    """
    {
    'a_m_city_latitude': '57.776543',
    'a_m_city_longitude': '26.004789',
    'a_m_country': 'Latvia',
    'a_m_name_of_local_authority': '-',
    'a_population_size': '9970',
    'b_city_background': '-',
    'b_climate_impacts_additional_information': '-',
    'b_m_climate_impacts': ['Flooding', 'Forest Fires', 'Ice and Snow', 'Storms'],
    'b_m_covenant_of_mayors_signatory': 'Yes',
    'b_m_current_status_of_mayors_adapt_enrolment': 'Already signed',
    'b_m_name_surname_of_mayor': 'Vents Armands Krauklis',
    'b_m_official_email': 'novads@valka.lv',
    'b_m_r_email_of_contact_person': 'cityprofiles@mayors-adapt.eu',
    'b_m_r_name_surname_of_contact_person': 'Gunta Smane',
    'b_m_role_of_contact_person': 'Head of Development and Planning Department',
    'b_m_sector': ['Agriculture and Forest', 'Biodiversity', 'Disaster Risk Reduction', 'Financial', 'Health', 'Infrastructure', 'Urban', 'Water Management'],
    'b_m_telephone': '+37126463408',
    'b_m_website_of_the_local_authority': 'http://www.valka.lv',
    'b_sector_additional_information': '-',
    'b_signature_date': '1435190400000',
    'c_m_stage_of_the_implementation_cycle': 'Preparing the ground',
    'd_adaptation_strategy_date_of_approval': '1435190400000',
    'd_adaptation_strategy_name': u'Development Strategy 2015 \u2013 2022',
    'd_adaptation_strategy_summary': u'The Development Strategy 2015 \u2013 2022 of the Municipality of Valka is a strategic document that establishes objectives and priorities for sustainable and integrated socio-economic development. The Strategy contains the vision, objectives, and priorities of the development of municipality, the investment plan necessary for the realisation of the Strategy, and a monitoring and evaluation system. While climate change adaptation is not the focus of the Development Strategy, the creation of a Local Adaption Strategy of Valka Municipality is planned.',
    'd_adaptation_strategy_weblink': 'http://valka.lv/pasvaldiba/dokumenti/attistibas-programma/',
    'd_m_developed_an_adaptationstrategy': 'No, Mayors Adapt is the first example of my city considering adaptation and we will develop an adaptation strategy',
    'e_adaptation_weblink': 'http://valka.lv/pasvaldiba/dokumenti/attistibas-programma/',
    'e_additional_information_on_adaptation_responses': '-',
    'e_m_motivation': "The main current impact of the climate changes to Valka's territory is the changing in the natural environment as well as social and economic consequences (including damaging economic infrastructure). By identifying and adapting to the current and future impacts of climate change, Valka hopes to strengthen its resilience to these changes, reduce the costs of damage, protect livelihoods, create jobs, and promote economic growth in the region.",
    'e_m_planed_adaptation_actions': 'The Adaption Strategy of Valka will define concrete actions that tackle problems related to climate change (for example, detailed measures for floods, forest fires, air quality and temperature).',
    'f_m_action_event_long_description': u'Valka is actively working to increase energy efficiency and the use of energy from renewable sources but such efforts also have adaptation\u2013related benefits. One of  the most important activities involves complex energy saving measures for public educational institutions (Valka Music School, Valka Primary School and Valka Sport Hall) and apartment buildings. The energy efficiency and heat resistance measures implemented include insulating facades and roofs; replacing windows, doors, and floors; renewing heating systems; reconstructing lighting and electrical power systems; and installing ventilation systems. By renovating buildings, Valka is also improving their resistance to the impacts of extreme temperatures.',
    'f_m_action_event_title': 'Improving of the heat resistance of municipal buildings',
    'f_picture_caption': "Valka's renovated Sports Hall",
    'f_sectors_concerned': ['Financial', 'Energy', 'Urban'],
    'h_m_elements': 'Sector Policies',
    'image': '11288937'
    }
    """

    l2k_countries_dict = {v: k for k, v in ace_countries_dict.iteritems()}
    l2k_stage_implementation_cycle = {
        i[1]: i[0] for i in _stage_implementation_cycle}
    l2k_status_of_adapt_signature = {
        i[1]: i[0] for i in _status_of_adapt_signature}
    l2k_climate_impacts = {
        t.title: t.value for t in aceitem_climateimpacts_vocabulary(container)}
    l2k_developed_an_adaptationstrategy = {
        i[1]: i[0] for i in _already_devel_adapt_strategy}
    l2k_key_vulnerable_adapt_sector_vocabulary = {
        t.title: t.value for t in key_vulnerable_adapt_sector_vocabulary(container)}
    l2k_sectors_concerned = {
        t.title: t.value for t in key_vulnerable_adapt_sector_vocabulary(container)}
    l2k_elements = {
        t.title: t.value for t in aceitem_elements_vocabulary(container)}

    def impacted_sectors(sectors):
        sectors_dict = l2k_key_vulnerable_adapt_sector_vocabulary
        return [sectors_dict[sect]
                for sect in data['b_m_sector'] if sect in sectors_dict]

    _map = {
        'a_m_city_latitude': {'newkey': 'city_latitude'},
        'a_m_city_longitude': {'newkey': 'city_longitude'},
        'a_m_country': {
            'newkey': 'country',
            'mapping_fnc': lambda x: l2k_countries_dict.get(x)},
        'a_m_name_of_local_authority': {'newkey': 'name_of_local_authority'},
        'a_population_size': {'newkey': 'population_size'},
        'b_m_climate_impacts': {
            'newkey': 'climate_impacts',
            'mapping': lambda x: l2k_climate_impacts.get(x)},
        'b_climate_impacts_additional_information': {
            'newkey': 'additional_information_on_climate_impacts'},
        'b_m_covenant_of_mayors_signatory': {'newkey': 'covenant_of_mayors_signatory'},
        'b_m_current_status_of_mayors_adapt_enrolment': {
            'newkey': 'status_of_mayors_adapt_signature',
            'mapping_fnc': lambda x: l2k_status_of_adapt_signature.get(x)},
        'b_m_name_surname_of_mayor': {'newkey': 'name_surname_of_mayor'},
        'b_m_official_email': {'newkey': 'official_email'},
        'b_m_sector': {
            'newkey': 'key_vulnerable_adaptation_sector',
            'mapping_fnc': impacted_sectors},
        'b_m_r_email_of_contact_person': {'newkey': 'e_mail_of_contact_person'},
        'b_m_r_name_surname_of_contact_person': {'newkey': 'name_surname_of_contact_person'},
        'b_m_role_of_contact_person': {'newkey': 'role_of_contact_person'},
        'b_m_telephone': {'newkey': 'telephone'},
        'b_m_website_of_the_local_authority': {'newkey': 'website_of_the_local_authority'},
        'b_signature_date': {
            'newkey': 'signature_date',
            'mapping_fnc': lambda x: dt.fromtimestamp(int(x) / 1e3).date()},
        'c_m_stage_of_the_implementation_cycle': {
            'newkey': 'stage_of_the_implementation_cycle',
            'mapping_fnc': lambda x: l2k_stage_implementation_cycle.get(x)},
        'd_adaptation_strategy_date_of_approval': {
            'newkey': 'date_of_approval_of_the_strategy__plan',
            'mapping_fnc': lambda x: dt.fromtimestamp(int(x) / 1e3).date()},
        'd_adaptation_strategy_name': {'newkey': 'name_of_the_strategy__plan'},
        'd_adaptation_strategy_summary': {'newkey': 'short_content_summary_of_the_strategy__plan'},
        'd_adaptation_strategy_weblink': {'newkey': 'weblink_of_the_strategy__plan'},
        'd_m_developed_an_adaptationstrategy': {
            'newkey': 'have_you_already_developed_an_adaptation_strategy',
            'mapping_fnc': lambda x: l2k_developed_an_adaptationstrategy.get(x)},
        'e_additional_information_on_adaptation_responses': {'newkey': 'additional_information_on_adaptation_responses'},
        'f_picture_caption': {'newkey': 'picture_caption'},
        'f_sectors_concerned': {
            'newkey': 'what_sectors_are_concerned',
            'mapping_fnc': lambda x: l2k_sectors_concerned.get(x)
        },
        'h_m_elements': {
            'newkey': 'adaptation_elements',
            'mapping_fnc': lambda x: l2k_elements.get(x)},
        # 'b_city_background': {'newkey': 'city_background'},
        # 'b_sector_additional_information': {'newkey': 'sector_additional_information'},
        # XXX: this seems to be duplicated with d_adaptation_strategy_weblink
        # 'e_adaptation_weblink': {'newkey': 'developed_an_adaptationstrategy'},
        # 'e_m_motivation': {'newkey': 'motivation'},
        # 'e_m_planed_adaptation_actions': {'newkey': 'planed_adaptation_actions'},
        # 'f_m_action_event_long_description': {'newkey': 'action_event_long_description'},
        # 'f_m_action_event_title': {'newkey': 'action_event_title'},
    }

    missing_vals = []
    for _type, name, payload in vals:
        if name not in _map:
            missing_vals.append((_type, name, payload))
    for v in missing_vals:
        print v

    # #fields in xml file
    # 'additional_information_on_adaptation_responses',
    # 'additional_information_on_climate_impacts',
    # 'additional_information_on_vulnerable_sectors',
    # 'city_background_information_about_the_city',
    # 'city_latitude',
    # 'city_longitude',
    # 'climate_impacts_risks_particularly_for_city_region',
    # 'country',
    # 'covenant_of_mayors_signatory',
    # 'date_of_approval_of_the_strategy__plan',
    # 'description',
    # 'e_mail_of_contact_person',
    # 'have_you_already_developed_an_adaptation_strategy',
    # 'key_vulnerable_adaptation_sector',
    # 'main_motivation_for_taking_adaptation_action',
    # 'name_and_surname_of_contact_person',
    # 'name_and_surname_of_mayor',
    # 'name_of_local_authority',
    # 'name_of_the_strategy__plan',
    # 'official_email',
    # 'picture',
    # 'picture_caption',
    # 'planned_current_adaptation_actions_and_responses',
    # 'population_size',
    # 'role_of_contact_person',
    # 'searchable',
    # 'short_content_summary_of_the_strategy__plan',
    # 'signature_date',
    # 'stage_of_the_implementation_cycle',
    # 'status_of_mayors_adapt_signature',
    # 'telephone',
    # 'title_of_the_action_event',
    # 'weblink_of_the_strategy__plan',
    # 'weblinks_to_relevant_plans_studies',
    # 'website_of_the_local_authority',
    # 'what_sectors_are_concerned',
    # 'which_elements_are_mentioned_in_your_city_profile'

    city_name = strip_xml(journal.title)
    mapped_data = {'title': city_name}
    for key in data:
        if key in _map:
            mapping = _map[key]
            newkey = mapping['newkey']
            if 'mapping_fnc' in mapping:
                fnc = mapping['mapping_fnc']
                val = fnc(data[key])
            else:
                val = data[key]
            mapped_data[newkey] = val
    city = createAndPublishContentInContainer(
        container,
        'eea.climateadapt.city_profile',
        id=journal.urltitle,
        **mapped_data
    )
    pprint.pprint(mapped_data)
    logger.info("Imported city profile %s", city_name)
    return city


def import_city_profiles(site):
    template_pks = {}
    for data in session.query(sql.Ddmtemplate):
        name = strip_xml(data.name)
        template_pks[name] = data.templatekey

    _id = template_pks['City Profile']
    cp = defaultdict(lambda:[])
    query = session.query(sql.Journalarticle).filter_by(templateid=_id)

    for data in query:
        name = strip_xml(data.title)
        cp[name].append(data)

    to_import = []

    for city_name in cp:
        if city_name and city_name != '-':
            cities = cp[city_name]
            cities.sort(key=lambda d:d.version)
            to_import.append(cities[-1])

    city_profiles_folder = createAndPublishContentInContainer(
        site,
        'Folder',
        id='city-profile',
        title='City Profiles',
    )
    imported = []
    for data in to_import:
        obj = import_city_profile(city_profiles_folder, data)
        imported.append(obj)

    return imported


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
    # DONE, parent name fixed

    # column-1 has a table with links and a table with info
    # column-2 has an iframe
    # Only one page: http://adapt-test.eea.europa.eu/tools/urban-adaptation/my-adaptation

    # assert(len(structure) == 3)
    # assert(len(structure['column-1']) == 2)
    # assert(len(structure['column-2']) == 1)

    main_title = structure.pop('name')
    cover = create_cover_at(site, layout.friendlyurl,
                            title=strip_xml(main_title))
    cover.aq_parent.edit(title=main_title)  # Fix parent name
    stamp_cover(cover, layout)

    tiles = []

    column_names = ['column-1', 'column-2', 'column-3', 'column-4', 'column-5']

    for name in column_names:   # Try to preserve the order of columns
        col = structure.get(name)
        if col:
            tiles.extend([make_tile(cover, [p], no_titles=True) for p in col])

    layout = make_layout(make_row(*[make_group(12, tile) for tile in tiles]))
    layout = json.dumps(layout)
    cover.cover_layout = layout

    return cover


@log_call
def import_template_transnationalregion(site, layout, structure):
    # DONE, parent title fixed

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

    main_content = render_tabs(payload)

    cover = create_cover_at(site, layout.friendlyurl, title=country['name'])
    cover.aq_parent.edit(title=structure['name'])
    stamp_cover(cover, layout)

    #image_tile = make_image_tile(site, cover, image_info)    # TODO: import image
    image = get_image_by_imageid(site, image_info['id'])
    image_tile = make_countries_dropdown_tile(cover, image)
    content_tile = make_richtext_tile(cover, {'title': 'main content',
                                              'text': main_content})

    image_group = make_group(2, image_tile)
    content_group = make_group(10, content_tile)

    layout = make_layout(make_row(image_group, content_group))
    cover.cover_layout = json.dumps(layout)
    return cover


@log_call
def import_template_ace_layout_2(site, layout, structure):
    # Done, parent title fixed

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
    stamp_cover(cover, layout)

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
        'thumb': localize(image, site) + "/@@images/image",
    }

    cover.aq_parent.edit(title=main['title'])   # Fix cover parent title

    main_content = render('templates/richtext_readmore_and_image.pt',
                          {'payload': main})

    main_content_tile = make_richtext_tile(cover, {'title': 'main content',
                                                   'text': main_content})

    col2_tile = make_tile(cover, structure['column-2'], 'col-md-4')
    col3_tile = make_tile(cover, structure['column-3'], 'col-md-4')

    relevant_content_tiles = [col2_tile, col3_tile]
    sidebar_tile = make_tile(cover, structure['column-4'])
    sidebar_group = make_group(3, sidebar_tile)
    main_content_group = make_group(9,
                                    main_content_tile, *relevant_content_tiles)
    layout = make_layout(make_row(main_content_group, sidebar_group))
    layout = json.dumps(layout)

    cover.cover_layout = layout
    return cover


@log_call
def import_template_ace_layout_col_1_2(site, layout, structure):
    # done, parent title fixed

    # TODO: fix the iframe, it's too small

    # this is a 2 column page with some navigation on the left and a big
    # iframe (or just plain html text) on the right
    # example page: http://adapt-test.eea.europa.eu//tools/urban-adaptation/climatic-threats/heat-waves/sensitivity

    assert(len(structure) == 3)
    assert(len(structure['column-1']) == 1)

    title = strip_xml(structure['name'])
    cover = create_cover_at(site, layout.friendlyurl, title=title)
    stamp_cover(cover, layout)
    cover.aq_parent.edit(title=title)   # Fix parent folder title

    urban_menu_tile = make_urbanmenu_title(cover)
    urban_menu_group = make_group(2, urban_menu_tile)

    top_nav = structure['column-1'][0][1]['content'][0]
    info = {
        'title': 'navigation',
        'text': top_nav,
        'css_class': 'tools-nav-menu',
    }
    top_nav_tile = make_richtext_tile(cover, info)

    main_tiles = [make_tile(cover, [portlet])
                  for portlet in structure['column-3']]

    nav_group = make_group(12, top_nav_tile)
    main_group = make_group(10, *main_tiles)

    first_row = make_row(nav_group)
    second_row = make_row(urban_menu_group, main_group)

    layout = make_layout(first_row, second_row)
    layout = json.dumps(layout)

    cover.cover_layout = layout

    return cover


@log_call
def import_template_ace_layout_3(site, layout, structure):
    # done, parent title fixed

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
            try:
                main['image'] = {'id': line[2][0]}
                continue
            except IndexError:
                main['image'] = {'id': None}
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
    stamp_cover(cover, layout)
    cover.aq_parent.edit(title=main['title'])    # Fix cover's parent title

    if layout.themeid == "balticseaace_WAR_acetheme":
        # TODO: mark the content with a special interface to enable the menu
        alsoProvides(cover, IBalticRegionMarker)

    main['image'].update({'title': '', 'thumb': ''})
    if main['image']['id']:
        image = get_image_by_imageid(site, main['image']['id'])
        if image is not None:
            main['image'].update({
                'title': image.Title(),
                'thumb': localize(image, site) + "/@@images/image",
            })

    main_content = render('templates/richtext_readmore_and_image.pt',
                          {'payload': main})

    main_content_tile = make_richtext_tile(cover, {'title': 'main content',
                                                   'text': main_content,
                                                   })
    relevant_content_tiles = [
        make_tile(cover, col, css_class='col-md-4') for col in extra_columns
    ]

    sidebar_tile = make_aceitem_search_tile(cover, sidebar[0][1])
    sidebar_group = make_group(3, sidebar_tile)
    main_content_group = make_group(9,
                                    main_content_tile, *relevant_content_tiles)
    layout = make_layout(make_row(main_content_group, sidebar_group))
    cover.cover_layout = json.dumps(layout)
    cover._p_changed = True

    return cover


@log_call
def import_template_ace_layout_4(site, layout, structure):
    # done, parent title fixed

    # TODO: the facts is not saved properly? shows labels instead of values

    # these are Project pages such as http://adapt-test.eea.europa.eu/web/guest/project/climsave

    title = structure['name']
    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover.aq_parent.edit(title=title)
    stamp_cover(cover, layout)

    main = {
        'accordion': [],
    }
    labels = {
        'Challenge': 'The Challenge',
        'Objective': "Project objectives",
        'Methodology': "Methodology",
        'Results': 'Results',
        'ProjectPartners': 'Project partners',
        'Deliverables': 'Deliverables',
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
            main['accordion'].append((labels[category], text))
            continue
        if line[0] == 'dynamic' and line[1] == 'ProjectPartner':
            name = line[2][0][2][0]
            symbol = line[2][1][2][0]
            if name:
                partners.append((name, symbol))

    main['accordion'].append(('Project Partners', partners))

    _main_sidebar = structure['column-2'][0][1]['content']
    sidebar_title = structure['column-2'][0][1]['portlet_title']

# [('dynamic', 'Instrument', ['FP7, Small-medium-sized Integrated Project']),
#  ('dynamic', 'StartDate', ['01/01/2010']),
#  ('dynamic', 'Duration', ['42 months']),
#  ('dynamic', 'ProjectCoord', ['Chancellor, Master and Scholars of the University of Oxford (United Kingdom)']),
#  ('dynamic', 'ProjectWebSite', ['www.climsave.eu']),
#  ('dynamic',
#   'Contact',
#   [('dynamic', 'ContactName', ['Dr. Paula Harrison']),
#    ('dynamic', 'ContactInstitute', ['Environmental Change Institute\nUniversity of Oxford']),
#    ('dynamic', 'ContactAddress', ['Oxford University Centre for the Environment, South Parks Road, Oxford, OX1 3QY, UK']),
#    ('dynamic', 'ContactMail', ['paharriso@aol.com']),
#

    print _main_sidebar

    _sidebar = []
    _contact = []
    for dyn, name, payload in _main_sidebar:
        if len(payload) == 1:
            _sidebar.append((name, payload[0]))
        else:
            for l in payload:
                if l:
                    _contact.append((l[1], l[2][0]))

    labels = {
        'Instrument': 'Instrument',
        'StartDate': 'Start date',
        'Duration': 'Duration',
        'ProjectCoord': 'Project Coordinator',
        'ProjectWebSite': 'Project website',
        'ContactPoint': "Contact Point",
    }

    contact_text = render("templates/snippet_contact.pt", {'lines': _contact,
                                                           'labels': labels})
    _sidebar.append(('ContactPoint', contact_text))
    sidebar_text = render("templates/snippet_sidebar_text.pt",
                          {'lines': _sidebar, 'labels': labels})
    sidebar_tile = make_richtext_with_title_tile(
        cover, {'title': sidebar_title, 'text': sidebar_text})

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
                       {'image': localize(image, site) + "/@@images/image",
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

    return cover


@log_call
def import_template_ast(site, layout, structure):
    # done
    # TODO: AST navigation menu
    # TODO: portlets order is not preserved?

    # column-1 has the imagemap on the left side
    # column-2 has 2 portlets:  title and then the one with content (which also
    # has a title)

    return _import_template_urban_ast(site, layout, structure,
                                      make_ast_navigation_tile,
                                      is_urbanast=False)


@log_call
def import_template_urban_ast(site, layout, structure):
    return _import_template_urban_ast(site, layout, structure,
                                      make_urbanast_navigation_tile,
                                      is_urbanast=True)


def _import_template_urban_ast(site, layout, structure, nav_tile_maker,
                               is_urbanast=False):
    # parent name fixed

    # column-1 has the imagemap on the left side
    # column-2 has 2 portlets:  title and then the one with content (which also
    # has a title)
    # there can be more columns where there are tiles with search

    assert(len(structure) >= 3)
    assert(len(structure['column-1']) == 1)
    assert(len(structure['column-2']) >= 2)

    image_portlet = structure['column-1'][0][1]['content'][0]
    portlet = structure['column-2'][1][1]

    #cover_title = structure['name']    # this will be the title
    section_title = portlet['portlet_title']
    main_section_title = structure['column-2'][0][1]['headertext']
    step = structure['column-2'][0][1]['step']

    main_text = make_text_from_articlejournal(portlet['content'])

    payload = {
        'title': main_section_title,
        'subtitle': section_title,
        'main_text': main_text
    }
    main_content = render('templates/ast_text.pt', payload)

    cover = create_cover_at(site, layout.friendlyurl, title=section_title)
    cover.aq_parent.edit(title=structure['name'])   # Fix parent name
    stamp_cover(cover, layout)

    # fix the scripts and css paths from this tile
    image_portlet = image_portlet.replace("/ace-theme/css/", "/++theme++climateadapt/static/")
    image_portlet = image_portlet.replace("/ace-theme/js/",  "/++theme++climateadapt/static/")
    image_portlet = image_portlet.replace("jquery.qtip.min.css", "jquery.qtip.css")

    image_tile = make_richtext_tile(cover, {'text': image_portlet,
                                            'title': 'AST Image'})
    main_content_tile = make_richtext_tile(cover, {'text': main_content,
                                                   'title': 'Main text'})
    # nav_tile = make_richtext_tile(cover, {'text': 'nav here', 'title': 'nav'})
    nav_tile = nav_tile_maker(cover)

    side_group = make_group(4, image_tile, nav_tile)

#  u'column-2': [(u'astheaderportlet_WAR_ASTHeaderportlet_INSTANCE_AQlGpTEbY3Eg',
#                 {'headertext': u'Implementation',
#                  'portletSetupCss': u'{"wapData":{"title":"","initialWindowState":"NORMAL"},"spacingData":{"margin":{"sameForAll":true,"bottom":{"unit":"px","value":""},"left":{"unit":"px","value":""},"right":{"unit":"px","value":""},"top":{"unit":"px","value":""}},"padding":{"sameForAll":true,"bottom":{"unit":"px","value":""},"left":{"unit":"px","value":""},"right":{"unit":"px","value":""},"top":{"unit":"px","value":""}}},"borderData":{"borderStyle":{"sameForAll":true,"bottom":"","left":"","right":"","top":""},"borderColor":{"sameForAll":true,"bottom":"","left":"","right":"","top":""},"borderWidth":{"sameForAll":true,"bottom":{"unit":"px","value":""},"left":{"unit":"px","value":""},"right":{"unit":"px","value":""},"top":{"unit":"px","value":""}}},"textData":{"fontWeight":"","lineHeight":"","textDecoration":"","letterSpacing":"","color":"","textAlign":"","fontStyle":"","fontFamily":"","wordSpacing":"","fontSize":""},"bgData":{"backgroundPosition":{"left":{"unit":"px","value":""},"top":{"unit":"px","value":""}},"backgroundColor":"","backgroundRepeat":"","backgroundImage":"","useBgImage":false},"advancedData":{"customCSS":"","customCSSClassName":""}}',
#                  'portletSetupShowBorders': u'false',
#                  'portletSetupUseCustomTitle': u'false',
#                  'step': u'5'}),


    [structure.pop(z) for z in ['column-1', 'column-2', 'name']]
    if structure:
        second_row_group = [make_group(6, t) for t in
                            [make_tile(cover, x) for x in structure.values()]
                            ]
        second_row = make_row(*second_row_group)
        if is_urbanast:
            tile = make_view_tile(cover,
                                        {'title': 'UrbanAST nav',
                                         'view_name': 'urbanast_bottom_nav'})
            third_row = make_group(8, tile)
            main_group = make_group(8, main_content_tile, second_row, third_row)
        else:
            main_group = make_group(8, main_content_tile, second_row)
    else:
        main_group = make_group(8, main_content_tile)

    layout = make_layout(make_row(side_group, main_group))
    cover.cover_layout = json.dumps(layout)
    cover._ast_navigation_step = int(step)
    cover._ast_title = main_section_title

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
    # done, parent title fixed

    # ex page: /share-your-info/general

    # row 1: text + image
    # row 2: share button

    assert(len(structure) == 2 or len(structure) == 3)
    assert(len(structure['column-1']) == 1)
    if len(structure) > 2:
        assert(len(structure['column-2']) == 1)

    content_portlet = structure['column-1'][0][1]['content']
    for bit in content_portlet:
        if bit[0] == 'image':
            image = bit[-1][0]
        if bit[0] == 'text':
            body = bit[-1][0]
        if bit[0] == 'dynamic' and bit[1] == 'Title':
            title = bit[-1][0]

    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover.setLayout('standard')
    alsoProvides(cover, IClimateAdaptSharePage)
    stamp_cover(cover, layout)

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
        parent_title = dict(_cca_types)[sharetype]
        cover.aq_parent.edit(title=parent_title)    # Fix parent title
    else:
        cover.aq_parent.edit(title=structure['name'])

    main_text_group = make_group(8, main_text_tile)
    image_group = make_group(4, image_tile)
    row_1 = make_row(main_text_group, image_group)

    if share_portlet:
        row_2 = make_row(make_group(12, share_tile))
        layout = make_layout(row_1, row_2)
    else:
        layout = make_layout(row_1)

    cover.cover_layout = json.dumps(layout)

    return cover


@log_call
def import_template_1_column(site, layout, structure):
    # done, fixed parent title
    # this is a simple page, with one portlet of text
    # example: /eu-adaptation-policy/funding/life

    if structure['column-1'][0][0] in portlet_importers:
        importer = portlet_importers.get(structure['column-1'][0][0])
        return importer(layout, structure)

    assert len(structure) == 2  # main portlet + layout name

    try:
        dict(structure['column-1'][0][1])
    except:
        logger.error("Invalid page structure for %s", layout.friendlyurl)
        return

    # There are three versions of this template:
    # - only one iframe
    # - two columns with an iframe below
    # - several portlets (with rich text) one below another

    cover_title = unicode(structure['name'])

    # try to get the main title and set it on the parent folder
    portlet_title = structure['column-1'][0][1].get('portlet_title')
    if portlet_title:
        main_title = portlet_title
    else:
        main_title = structure['column-1'][0][1].get('title') or ""
    main_title = strip_xml(main_title) or cover_title

    cover = create_cover_at(site, layout.friendlyurl, title=cover_title)
    cover.aq_parent.edit(title=main_title)  # Fix parent title
    if layout.friendlyurl in additional_sharepage_layouts:
        alsoProvides(cover, IClimateAdaptSharePage)
    stamp_cover(cover, layout)

    def _import_two_columns():
        content = structure['column-1'][0][1]['content']

        col1 = u"".join(content)
        col2 = u"".join(structure['column-1'][1][1]['content'][0])

        col1_tile = make_richtext_tile(cover, {'title': 'col1', 'text': col1})
        col2_tile = make_richtext_tile(cover, {'title': 'col1', 'text': col2})
        iframe = structure['column-1'][2][1]['url']
        iframe_tile = make_iframe_embed_tile(cover, iframe)

        col1_group = make_group(6, col1_tile)
        col2_group = make_group(6, col2_tile)
        iframe_group = make_group(12, iframe_tile)

        row_1 = make_row(col1_group, col2_group)
        row_2 = make_row(iframe_group)
        layout = make_layout(row_1, row_2)
        return layout

    def _import_cols():
        content = structure['column-1'][0][1]['content']

        if isinstance(content[0], tuple):
            # this is a dynamic portlet
            logger.warning("Please investigate this importer %s with template %s",
                        layout.friendlyurl, '1_column')
            return

        tiles = [make_tile(cover, [p]) for p in structure['column-1']]

        main_group = make_group(12, *tiles)
        cover_layout = make_layout(make_row(main_group))
        return cover_layout

    def _import_iframe():
        tiles = [make_tile(cover, [p]) for p in structure['column-1']]
        main_group = make_group(12, *tiles)
        cover_layout = make_layout(make_row(main_group))
        cover.setLayout('standard')

        return cover_layout
    if layout.friendlyurl == u'/tools/urban-ast/contact':
        form_tile = make_tile(cover, structure.get('column-1', []))
        form_group = make_group(12, form_tile)
        cover_layout = make_layout(make_row(form_group))

    elif 'content' not in structure['column-1'][0][1]:
        # an iframe layout, such as /tools/map-viewer
        cover_layout = _import_iframe()
    elif len(structure['column-1']) > 2:
        cover_layout = _import_two_columns()
    else:
        cover_layout = _import_cols()

    cover.cover_layout = json.dumps(cover_layout)
    cover._p_changed = True
    return cover


@log_call
def import_template_2_columns_i(site, layout, structure):
    # done, fixed parent title

    # ex: /countries
    # TODO: fix images linking

    assert(len(structure) in [2, 3])

    title = structure['name']

    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover.aq_parent.edit(title=title)   # fix parent title
    stamp_cover(cover, layout)

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
        main_group = make_group(12, main_text_tile, countries_tile)
    else:
        main_group = make_group(12, main_text_tile)

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

    if len(structure) == 1:  # this is a fake page. Ex: /adaptation-sectors
        logger.warning("Please investigate this importer %s with template %s",
                       layout.friendlyurl, '2_columns_ii')
        return

    if layout.friendlyurl == u'/mayors-adapt/register':
        # this is the /mayors-adapt page
        title = structure['name']

        cover = create_cover_at(site, layout.friendlyurl, title=title)
        cover.aq_parent.edit(title=title)   # Fix parent title
        stamp_cover(cover, layout)
        form_tile = make_tile(cover, structure.get('column-1', []))
        image_tile = make_tile(cover, structure.get('column-2', []))
        side_group = make_group(6, form_tile)
        main_group = make_group(6, image_tile)
        layout = make_layout(make_row(side_group, main_group))

        cover.cover_layout = json.dumps(layout)
        cover.setLayout('no_title_cover_view')
        return cover


@log_call
def import_template_2_columns_iii(site, layout, structure):
    # done, fixed parent title

    # ex: /organisations

    assert(len(structure) == 2 or len(structure) == 3)

    #title = structure['name']
    title = structure['column-1'][0][1]['portlet_title']
    body = structure['column-1'][0][1]['content'][0]

    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover.aq_parent.edit(title=title)   # Fix parent title
    stamp_cover(cover, layout)

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
        side_group = make_group(5, image_tile)
        main_group = make_group(7, main_content_tile, *extra_tiles)
        layout = make_layout(make_row(main_group, side_group))
    else:
        main_group = make_group(12, main_content_tile)
        layout = make_layout(make_row(main_group))

    cover.cover_layout = json.dumps(layout)
    cover.setLayout('standard')
    return cover


@log_call
def import_template_ace_layout_1(site, layout, structure):
    # ex page: /home (may be just a mockup for home page)
    logger.warning("Please investigate this importer %s with template %s",
                   layout.friendlyurl, 'ace_layout_1')


@log_call
def import_template_ace_layout_5(site, layout, structure):
    # done, fixed parent title
    # ex page: /transnational-regions/caribbean-area
    # 1 row, 2 columns. First column: image + region selection tile
    #                   Second column: rich text

    assert(len(structure) == 4)
    assert(len(structure['column-1']) == 1)

    _titles = {
        'policy_legal_framework': "Policy and legal framework",
        'assessments_and_projects': "Assessments and projects",
    }

    main_title = structure['name']
    image = structure['column-1'][0][1]['content'][0][2][0]
    main_text = ""

    texts = structure['column-2'][0][1]['content']
    title = None
    if len(texts) > 1:
        for bit in texts:
            title = _titles[bit[1]]
            text = bit[2][0]
            main_text += u"<h3>{0}</h3>\n{1}".format(title, text)
    else:
        main_text = texts[0]

    cover = create_cover_at(site, layout.friendlyurl, title=title or main_title)
    cover.aq_parent.edit(title=main_title)
    alsoProvides(cover.aq_parent, ITransnationalRegionMarker)
    cover.aq_parent.reindexObject(idxs=('object_provides',))

    info = {'title': main_title, 'text': main_text }
    main_text_tile = make_richtext_with_title_tile(cover, info)

    main_text_group = make_group(9, main_text_tile)
    dropdown_tile = make_transregion_dropdown_tile(cover)
    image_info = {
        'id': image,
        'description': '',
        'title': 'region image',
    }
    image_tile = make_image_tile(site, cover, image_info)    # TODO: import image
    image_group = make_group(3, image_tile, dropdown_tile)
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

    # done, parent title fixed
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
    cover.aq_parent.edit(title=structure['name'])
    stamp_cover(cover, layout)
    cover.setLayout('standard')

    info = {'title': title, 'text': main_text}
    main_text_tile = make_richtext_tile(cover, info)
    main_text_group = make_group(12, main_text_tile)

    col_tiles = [
        make_richtext_tile(cover, {'text': col, 'title': 'column'})
        for col in [col1, col2, col3]
    ]
    row_1 = make_row(main_text_group)
    row_2 = make_row(*[make_group(4, t) for t in col_tiles])
    layout = make_layout(row_1, row_2)

    cover.cover_layout = json.dumps(layout)

    return cover


@log_call
def import_template_frontpage(site, layout, structure):
    """ Makes the frontpage cover for the site.

    Structure:

        * 1st row:
            * promotions carousel slideshow
        * 2nd row:
            * img tile: use ast support tool
            * img tile: countries dropdown
            * img tile: find case studies
            * img tile: share your information
        * 3rd row:
            * news listing tile
            * events listing tile
            * newsletter rich text tile
            * latest updates rich text tile
        * 4th row:
            eu sector policies tile
        * 5th row:
            * EU funding and adaptation tile
            * EU climate policy
    """
    cover = createAndPublishContentInContainer(
        site,
        'collective.cover.content',
        id='frontpage',
        title='Home'
    )
    cover.setLayout('no_title_cover_view')
    site.setLayout('frontpage')

    carousel_tile = make_view_tile(cover,
                                   {'title': 'Promotions',
                                    'view_name': 'fp-promotions-carousel-tile'})
    ast_tile = make_view_tile(cover,
                              {'title': 'AST',
                               'view_name': 'fp-ast-tile'})
    countries_tile = make_view_tile(cover,
                                    {'title': 'Countries',
                                     'view_name': 'fp-countries-tile'})
    casestudies_tile = make_view_tile(cover,
                                      {'title': 'Case studies',
                                       'view_name': 'fp-casestudies-tile'})
    shareinfo_tile = make_view_tile(cover,
                                    {'title': 'Share info',
                                     'view_name': 'fp-shareinfo-tile'})
    news_tile = make_view_tile(cover,
                               {'title': 'News',
                                'view_name': 'fp-news-tile'})
    events_tile = make_view_tile(cover,
                                 {'title': 'Events',
                                  'view_name': 'fp-events-tile'})

    newsletter_tile = make_view_tile(cover,
                                     {'title': "Newsletter",
                                      "view_name": "fp-newsletter-tile"})

    latest_updates_tile = make_view_tile(cover,
                                     {'title': "Latest updates",
                                      "view_name": "fp-latest-updates-tile"})

    eu_sector_policies_tile = make_view_tile(cover,
                                     {'title': "EU Sector Policies",
                                      "view_name": "fp-sector-policies-tile"})

    eu_funding_tile = make_view_tile(cover,
                                     {'title': "EU Funding and Adaptation",
                                      "view_name": "fp-funding-tile"})

    eu_climate_policy_tile = make_view_tile(cover,
                                     {'title': "EU Climate Policy",
                                      "view_name": "fp-climate-policy-tile"})


    row_1 = make_row(make_group(12, carousel_tile))
    row_2 = make_row(*[make_group(3, tile) for tile in [ast_tile,
                                                             countries_tile,
                                                             casestudies_tile,
                                                             shareinfo_tile]])
    row_3 = make_row(*[make_group(3, tile) for tile in
                           [news_tile, events_tile, newsletter_tile,
                            latest_updates_tile]])
    row_4 = make_row(make_group(12, eu_sector_policies_tile))
    row_5 = make_row(*[make_group(6, tile) for tile in [eu_funding_tile,
                                                        eu_climate_policy_tile]])

    layout = make_layout(row_1, row_2, row_3, row_4, row_5)
    layout = json.dumps(layout)

    cover.cover_layout = layout
    return cover


def run_importer(site=None):
    sql.Address = sql.Addres    # wrong detected plural
    fix_relations(session)

    if 'dbshell' in sys.argv:
        import pdb; pdb.set_trace()

    if site is None:
        site = get_plone_site()

    wftool = getToolByName(site, "portal_workflow")

    structure = [('content', 'Content'),
                 ('aceprojects', 'Projects'),
                 ('casestudy', 'Case Studies'),
                 ('adaptationoption', 'Adaptation Options'),
                 ('repository', 'Repository')
                 ]
    for name, title in structure:
        if name not in site.contentIds():
            site.invokeFactory("Folder", name)
            obj = site[name]
            obj.edit(title=title)
            try:
                wftool.doActionFor(obj, 'publish')
            except WorkflowException:
                logger.exception("Could not publish:" + obj.absolute_url(1))

    for image in session.query(sql.Image):
        import_image(image, site['repository'])

    for dlfileentry in session.query(sql.Dlfileentry):
        import_dlfileentry(dlfileentry, site['repository'])

    # for dlfileversion in session.query(sql.Dlfileversion):
    #     import_dlfileversion(dlfileversion, site['repository'])

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
            pass
            import_adaptationoption(acemeasure, site['adaptationoption'])

    for layout in session.query(sql.Layout).filter_by(privatelayout=False):
        try:
            cover = import_layout(layout, site)
        except:
            logger.exception("Couldn't import layout %s", layout.friendlyurl)
        if cover:
            cover._imported_comment = \
                "Imported from layout {0} - {1}".format(layout.layoutid,
                                                        layout.uuid_)
            logger.info("Created cover at %s", cover.absolute_url())


    import_journal_articles(site)
    tweak_site(site)


def import_journal_articles(site):

    parent = create_folder_at(site, '/more-events')
    create_plone_content(
        parent,
        type='Collection',
        title='Events',
        slug='events',
        sort_on=u'effective',
        sort_reversed=True,
        query=[{u'i': u'portal_type',
                u'o': u'plone.app.querystring.operation.selection.is',
                u'v': [u'Event']},
               {u'i': u'path',
                u'o': u'plone.app.querystring.operation.string.relativePath',
                u'v': u'..'}],)
    parent.setDefaultPage('events')

    for info in session.query(sql.Journalarticle).filter_by(type_='events'):
        latest = _get_latest_version(session, info)
        if latest.urltitle in parent.contentIds():
            logger.debug("Skipping %s, already imported", info.urltitle)
            continue

        slug = latest.urltitle
        title = strip_xml(latest.title)
        publish_date = latest.displaydate

        content = extract_simplified_info_from_article_content(latest.content)
        # content is in form:
        # [('dynamic', 'location', ['']),
        #   ('list', 'day', ['22']),
        #   ('list', 'month', ['May']),
        #   ('list', 'year', ['2014']),
        #   ('dynamic', 'url', ['http://www.interreg4c.eu/policy-sharing-policy-learning/overview/']),
        #   ('dynamic', 'title', ['Policy sharing, policy learning, Interreg IVC, Brussels, Belgium'])]

        if latest.structureid == 'ACEEVENT':
            attrs = {}
            for line in content:
                name = line[1]
                val = line[2][0]
                attrs[name] = val

            link = attrs['url']
            day = attrs['day']
            month = attrs['month']
            year = attrs['year']
            location = attrs['location']
            date = dateutil.parser.parse("{0} {1} {2}".format(day, month, year))
            date = utc.localize(date)

            event = create_plone_content(parent, type='Event', id=slug,
                                         title=title, location=location,
                                         start=date, end=date, whole_day=True,
                                         timezone='UTC',
                                         event_url=link, effective_date=publish_date)

            logger.info("Created Event at %s with effective %s" % (event.absolute_url(), str(publish_date)))
        else:
            print "no structure id"
            import pdb; pdb.set_trace()

    parent = create_folder_at(site, '/news-archive')
    create_plone_content(
        parent,
        type='Collection',
        title='News',
        slug='news',
        sort_on=u'effective',
        sort_reversed=True,
        query=[{u'i': u'portal_type',
                u'o': u'plone.app.querystring.operation.selection.is',
                u'v': [u'News Item']},
               {u'i': u'path',
                u'o': u'plone.app.querystring.operation.string.relativePath',
                u'v': u'..'}],)
    parent.setDefaultPage('news')

    for info in session.query(sql.Journalarticle).filter_by(type_='news'):
        # We get the latest version and skip it if it's already imported
        latest = _get_latest_version(session, info)

        if latest.urltitle in parent.contentIds():
            logger.debug("Skipping %s, already imported", info.urltitle)
            continue

        slug = latest.urltitle
        title = strip_xml(latest.title)
        publish_date = latest.displaydate

        content = extract_simplified_info_from_article_content(latest.content)
        if latest.structureid == 'ACENEWS':
            attrs = {}
            for line in content:
                name = line[1]
                val = line[2][0]
                attrs[name] = val
            link = attrs['url']
            #link_title = attrs['title']
            news = create_plone_content(parent, type='Link', id=slug,
                                        title=title, remoteUrl=link,
                                        effective_date=publish_date)
            logger.info("Created Link for news at %s with effective %s" % (news.absolute_url(), publish_date))
        else:
            text = content[0]
            news = create_plone_content(parent, type='News Item', id=slug,
                                        title=title, text=text,
                                        effective_date=publish_date)
            logger.info("Created News Item for news at %s", news.absolute_url())


def tweak_site(site):
    """ Apply any other tweaks to the site
    """

    ast_tools = ['tools/urban-ast',
                 'adaptation-support-tool']
    for path in ast_tools:
        obj = site.restrictedTraverse(path)
        if not IASTNavigationRoot.providedBy(obj):
            alsoProvides(obj, IASTNavigationRoot)

    faceted_pages = [
        ('/data-and-downloads', 'search.xml', 'faceted-climate-listing-view'),
    ]

    for location, xmlfilename, layout in faceted_pages:
        # TODO: also add a title
        make_faceted(site, location, xmlfilename, layout)

    # reorder providedBy for '/data-and-downloads'

    dad = site['data-and-downloads']
    dad.title = 'Search the database'
    noLongerProvides(dad, IFacetedNavigable)
    alsoProvides(dad, ISiteSearchFacetedView)
    faceted_view = getMultiAdapter((dad, site.REQUEST), name="faceted_subtyper")
    faceted_view.enable()
    IFacetedLayout(dad).update_layout('faceted-climate-listing-view')

    # TODO: create manually created pages
    # tweak frontpage portlets


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


def _make_session():
    engine = create_engine(os.environ.get("DB"))
    Session = scoped_session(sessionmaker(bind=engine))
    register(Session, keep_session=True)

    return Session()


def main():
    """ Run the ClimateAdapt import process

    This should be run through the zope client script running machinery, like so:

    DB=postgres://postgres:pwd@localhost/climate bin/www1 run bin/climateadapt_importer
    """
    global session
    session = _make_session()
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
    session = _make_session()

    site = context.getSite()
    run_importer(site)
