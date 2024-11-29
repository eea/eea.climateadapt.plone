# raise ValueError("Should not be imported")

import json
import os
import sys
from collections import defaultdict
from datetime import datetime as dt

import dateutil
import transaction
from eea.climateadapt._importer import sqlschema as sql
from eea.climateadapt._importer.tweak_sql import fix_relations
from eea.climateadapt._importer.utils import parse_settings  # , printe
from eea.climateadapt._importer.utils import (
    ACE_ITEM_TYPES, _get_latest_version, create_cover_at, create_folder_at,
    create_plone_content, createAndPublishContentInContainer,
    extract_portlet_info, extract_simplified_info_from_article_content,
    get_relateditems, get_repofile_by_id, localize, log_call, logger,
    make_ast_navigation_tile, make_countries_dropdown_tile, make_faceted,
    make_group, make_iframe_embed_tile, make_image_tile, make_layout,
    make_richtext_tile, make_richtext_with_title_tile, make_row,
    make_share_tile, make_tile, make_tiles, make_transregion_dropdown_tile,
    make_urbanast_navigation_tile, make_urbanmenu_title, make_view_tile,
    pack_to_table, r2t, render, render_accordion, render_tabs, s2d, s2l, s2li,
    stamp_cover, strip_xml, t2r, to_decimal, write_links)
from eea.climateadapt.config import DEFAULT_LOCATIONS
from eea.climateadapt.interfaces import (IASTNavigationRoot,
                                         IBalticRegionMarker,
                                         IClimateAdaptSharePage,
                                         ICountriesRoot, IMayorAdaptRoot,
                                         ISiteSearchFacetedView,
                                         ITransnationalRegionMarker,
                                         ITransRegioRoot)
from eea.climateadapt.vocabulary import (_cca_types, ace_countries_vocabulary,
                                         aceitem_climateimpacts_vocabulary,
                                         aceitem_elements_vocabulary,
                                         aceitem_sectors_vocabulary)
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from persistent.list import PersistentList
from plone.api import portal
from plone.api.content import move
# from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.file import NamedBlobFile, NamedBlobImage
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from pytz import timezone, utc
from html import unescape as html_unescape
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from z3c.relationfield.relation import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter, getUtility
from zope.interface import alsoProvides, noLongerProvides
from zope.intid.interfaces import IIntIds
from zope.sqlalchemy import register

# from eea.climateadapt.interfaces import ICitiesListingsRoot


ctz = timezone('Europe/Copenhagen')

session = None      # this will be a global bound to the current module

additional_sharepage_layouts = [
    '/share-your-info/indicators',
    '/share-your-info/map-graph-data'
]


@log_call
def import_aceitem(data, location):
    # TODO: Some AceItems have ACTION, MEASURE, REASEARCHPROJECT types and
    # should be mapped over AceMeasure and AceProject

    creationdate = data.creationdate

    if creationdate is not None:
        creationdate = creationdate.replace(tzinfo=ctz)

    approvaldate = data.approvaldate

    if approvaldate is not None:
        approvaldate = approvaldate.replace(tzinfo=ctz)

    related = get_relateditems(data, location)

    item = createAndPublishContentInContainer(
        location,
        ACE_ITEM_TYPES[data.datatype],
        title=data.name,
        long_description=t2r(data.description),
        keywords=s2l(r2t(data.keyword), separators=[';', ',']),
        spatial_layer=data.spatiallayer,
        spatial_values=s2l(data.spatialvalues),
        data_type=data.datatype,
        storage_type=data.storagetype,
        sectors=s2l(data.sectors_),
        elements=s2l(data.elements_),
        climate_impacts=s2l(data.climateimpacts_),
        websites=s2l(r2t(html_unescape(data.storedat)),
                     separators=[';', ',']),
        source=t2r(data.source),
        comments=data.comments,
        year=int(data.year or '0'),
        geochars=data.geochars,
        special_tags=s2l(data.specialtagging, relaxed=True),
        rating=data.rating,
        metadata=data.metadata_,
        creation_date=creationdate,
        effective_date=approvaldate,
        relatedItems=related,
        _publish=data.controlstatus == 1,
    )
    item._aceitem_id = data.aceitemid

    logger.debug("Imported aceitem %s from sql aceitem %s",
                 item.absolute_url(1), data.aceitemid)
    _fix_supdocs(item)
    item.reindexObject()

    return item


@log_call
def import_aceproject(data, location):
    creationdate = data.creationdate

    if creationdate is not None:
        creationdate = creationdate.replace(tzinfo=ctz)

    approvaldate = data.approvaldate

    if approvaldate is not None:
        approvaldate = approvaldate.replace(tzinfo=ctz)

    related = get_relateditems(data, location)

    item = createAndPublishContentInContainer(
        location,
        'eea.climateadapt.aceproject',
        title=data.title,
        acronym=data.acronym,
        lead=data.lead,
        websites=s2l(r2t(html_unescape(data.website))),
        long_description=t2r(data.abstracts),
        source=t2r(data.source),
        partners=t2r(data.partners),
        keywords=s2l(r2t(data.keywords), separators=[';', ',']),
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
        creation_date=creationdate,
        effective_date=approvaldate,
        relatedItems=related,
        _publish=data.controlstatus == 1,
    )

    item._aceproject_id = data.projectid
    _fix_supdocs(item)
    item.reindexObject()

    logger.debug("Imported aceproject %s from sql aceproject %s",
                 item.absolute_url(1), data.projectid)

    return item


def get_measure(id, context):
    """ Returns the measure based on imported id
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(acemeasure_id=id)

    if brains:
        return brains[0].getObject()
    else:
        logger.warning("Couldn't find measure id %s", id)


@log_call
def import_adaptationoption(data, location):

    creationdate = data.creationdate

    if creationdate is not None:
        creationdate = creationdate.replace(tzinfo=ctz)

    approvaldate = data.approvaldate

    if approvaldate is not None:
        approvaldate = approvaldate.replace(tzinfo=ctz)

    item = createAndPublishContentInContainer(
        location,
        'eea.climateadapt.adaptationoption',
        # adaptationoptions=measures,
        challenges=t2r(data.challenges),
        climate_impacts=s2l(data.climateimpacts_),
        comments=data.comments,
        contact=t2r(data.contact),
        cost_benefit=t2r(data.costbenefit),
        elements=s2l(data.elements_),
        geochars=data.geochars,
        implementation_time=t2r(data.implementationtime),
        implementation_type=data.implementationtype,
        # keywords=s2l(data.keywords, separators=[';', ',']),
        # keywords=t2r(data.keywords),
        keywords=s2l(r2t(data.keywords), separators=[';', ',']),
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
        year=int(data.year or '0'),
        # websites=s2l(data.website),
        websites=s2l(r2t(html_unescape(data.website))),
        governance_level=s2l(data.geos_),
        category=s2l(data.category),
        creation_date=creationdate,
        effective_date=approvaldate,
        _publish=data.controlstatus == 1,
    )
    item._acemeasure_id = data.measureid
    item.reindexObject()

    logger.debug("Imported adaptation option %s from sql acemeasure %s",
                 item.absolute_url(1), data.measureid)

    return item


@log_call
def import_casestudy(data, location):
    intids = getUtility(IIntIds)

    measure_ids = s2li(data.adaptationoptions) or []
    measures = [
        _f
        for _f in [get_measure(x, location) for x in measure_ids]
        if _f]
    measures = [RelationValue(intids.getId(m)) for m in measures]

    primephoto = None

    if data.primephoto:
        primephoto = get_repofile_by_id(location.aq_inner.aq_parent,
                                        data.primephoto)
    primephoto = primephoto and RelationValue(intids.getId(primephoto)) or None
    supphotos = []
    supphotos_str = data.supphotos is not None and data.supphotos or ''

    for supphotoid in supphotos_str.split(';'):
        supphoto = get_repofile_by_id(location, supphotoid)

        if supphoto:
            supphotos.append(RelationValue(intids.getId(supphoto)))

    related = get_relateditems(data, location)

    creationdate = data.creationdate

    if creationdate is not None:
        creationdate = creationdate.replace(tzinfo=ctz)

    approvaldate = data.approvaldate

    if approvaldate is not None:
        approvaldate = approvaldate.replace(tzinfo=ctz)

    latitude, longitude = to_decimal(data.lat), to_decimal(data.lon)
    geoloc = None

    # if latitude and longitude:
    #     geoloc = Geolocation(latitude=latitude, longitude=longitude)

    item = createAndPublishContentInContainer(
        location,
        'eea.climateadapt.casestudy',
        adaptationoptions=measures,
        challenges=t2r(data.challenges),
        climate_impacts=s2l(data.climateimpacts_),
        comments=data.comments,
        contact=t2r(data.contact),
        cost_benefit=t2r(data.costbenefit),
        elements=s2l(data.elements_),
        geochars=data.geochars,
        implementation_time=t2r(data.implementationtime),
        implementation_type=data.implementationtype,
        keywords=s2l(r2t(data.keywords), separators=[';', ',']),
        legal_aspects=t2r(data.legalaspects),
        lifetime=t2r(data.lifetime),
        geolocation=geoloc,
        long_description=t2r(data.description),
        measure_type=data.mao_type,
        objectives=t2r(data.objectives),
        primephoto=primephoto,
        rating=data.rating,
        year=int(data.year or '0'),
        relevance=s2l(data.relevance),
        sectors=s2l(data.sectors_),
        solutions=t2r(data.solutions),
        source=t2r(data.source),
        spatial_layer=data.spatiallayer,
        spatial_values=s2l(data.spatialvalues),
        stakeholder_participation=t2r(data.stakeholderparticipation),
        success_limitations=t2r(data.succeslimitations),
        supphotos=supphotos,
        title=data.name,
        websites=s2l(r2t(html_unescape(data.website))),
        creation_date=creationdate,
        effective_date=approvaldate,
        relatedItems=related,
        _publish=data.controlstatus == 1,
    )

    item._acemeasure_id = data.measureid
    item.reindexObject()

    _fix_supdocs(item)

    logger.debug("Imported casestudy %s from sql acemeasure %s",
                 item.absolute_url(1), data.measureid)

    return item


@log_call
def import_image(data, location):
    name = "{0}.{1}/1.0".format(data.imageid, data.type_)
    # str(data.imageid) + '.' + data.type_ + '/1.0'
    try:
        file_data = open('./document_library/0/0/' + name).read()
    except IOError:
        logger.error("Image with id %d does not exist in the supplied "
                     "document library", data.imageid)

        return None

    filename = str("{0}.{1}".format(data.imageid, data.type_))
    item = createAndPublishContentInContainer(
        location,
        'Image',
        title='Image {0}'.format(filename),
        id=filename,
        image=NamedBlobImage(filename=filename, data=file_data)
    )
    info = list(map(str, [data.imageid]))
    IAnnotations(item)['eea.climateadapt.imported_ids'] = PersistentList(info)

    item.reindexObject()
    logger.debug("Imported image %s from sql Image %s",
                 item.absolute_url(1), data.imageid)

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
    elif data.treepath == '/0/':
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
    # filename = str(data.name) + '.' + data.extension
    filename = str("{0}.{1}".format(data.fileentryid, data.extension))

    if 'jpg' in data.extension or 'png' in data.extension:
        item = createAndPublishContentInContainer(
            location,
            'Image',
            title=data.title,
            description=data.description,
            id=filename,
            image=NamedBlobImage(filename=filename, data=file_data)
        )
    else:
        item = createAndPublishContentInContainer(
            location,
            'File',
            title=data.title,
            description=data.description,
            id=filename,
            file=NamedBlobFile(filename=filename, data=file_data)
        )

    # item._uuid = data.uuid_
    info = list(map(str, [data.uuid_,
                     data.name,
                     data.fileentryid,
                     data.largeimageid,
                     # data.smallimageid,
                     ]))
    IAnnotations(item)['eea.climateadapt.imported_ids'] = PersistentList(info)

    logger.debug("Imported %s from sql dlentry %s",
                 item.absolute_url(1), data.fileentryid)

    item.reindexObject()

    return item


no_import_layouts = [
    # '/documents',   # this is an internal Liferay page
    '/contact-us',  # this is a page that doesn't really exist in the db
    '/climate-hazards',  # this is a page that doesn't really exist in the db
    '/adaptation-sectors',  # this is a page that doesn't really exist in the db
    '/general',  # this is a page that doesn't really exist in the db
    '/good-practices',
    '/news-and-forum',
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
    '/countries',
    '/articles',
    '/countries-light',
    '/countries-medium',
    '/projects1',
    '/explain-ast-vul',
    '/city-profile-form',
    '/harvesters',
    '/data-and-downloads',
    '/aceitems1',
    '/city-profile',
    '/sat',
    '/news-archive',
    '/more-events',
    '/test',
    '/documents',
    '/sitemap',
    '/provant',
    '/adaptation-strategies',
    '/maintain',
    '/explain',
    '/6',
    '/links',
    '/home',
    '/newregion',
    '/content/eea-climateadapt-researchproject',
    '/mayors-adapt',
    '/newregion',
    '/map-viewer',  # TODO: add a browser view for this one
    '/content',
    '/transnational-regions',
    '/transnational-regions/bsr-adaptation-old',
    '/atlantic-area',
    '/atlantic-area1',
    '/more-latest-updates',
    '/news-archive',
]

# TO DO

#  /tools/map-viewer   Linkuri Interne
#  /tools/time-series-tool
# '/countries-regions',

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

    if layout.type_ == 'control-panel':
        # we skip control panel pages

        return

    if layout.friendlyurl in WATCH:
        import pdb
        pdb.set_trace()

    settings = parse_settings(layout.typesettings)

    if layout.type_ == 'link_to_layout':
        # TODO: warning: log this, they may create recursions
        llid = int(settings['linkToLayoutId'][0])
        ll = session.query(sql.Layout).filter_by(layoutid=llid).one()
        this_url = layout.friendlyurl
        child_url = ll.friendlyurl
        folder = create_folder_at(site, this_url)
        folder.setLayout(child_url.split('/')[-1])
        folder.title = strip_xml(ll.name)

        return folder

    template = settings['layout-template-id'][0]

    logger.debug("Importing layout %s at url %s with template %s",
                 layout.layoutid, layout.friendlyurl, template)

    def is_column(s): return (s.startswith('column-')
                              and not s.endswith('-customizable'))

    structure = {}

    structure['name'] = strip_xml(layout.name)

    for column, portlet_ids in [kv for kv in list(settings.items()) 
                                if is_column(kv[0])]:
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
    'd_adaptation_strategy_name': u'Development Strategy 2015 \\u2013 2022',
    'd_adaptation_strategy_summary': u'The Development Strategy 2015 \\u2013 2022 of the Municipality of Valka is a strategic document that establishes objectives and priorities for sustainable and integrated socio-economic development. The Strategy contains the vision, objectives, and priorities of the development of municipality, the investment plan necessary for the realisation of the Strategy, and a monitoring and evaluation system. While climate change adaptation is not the focus of the Development Strategy, the creation of a Local Adaption Strategy of Valka Municipality is planned.',
    'd_adaptation_strategy_weblink': 'http://valka.lv/pasvaldiba/dokumenti/attistibas-programma/',
    'd_m_developed_an_adaptationstrategy': 'No, Mayors Adapt is the first example of my city considering adaptation and we will develop an adaptation strategy',
    'e_adaptation_weblink': 'http://valka.lv/pasvaldiba/dokumenti/attistibas-programma/',
    'e_additional_information_on_adaptation_responses': '-',
    'e_m_motivation': "The main current impact of the climate changes to Valka's territory is the changing in the natural environment as well as social and economic consequences (including damaging economic infrastructure). By identifying and adapting to the current and future impacts of climate change, Valka hopes to strengthen its resilience to these changes, reduce the costs of damage, protect livelihoods, create jobs, and promote economic growth in the region.",
    'e_m_planed_adaptation_actions': 'The Adaption Strategy of Valka will define concrete actions that tackle problems related to climate change (for example, detailed measures for floods, forest fires, air quality and temperature).',
    'f_m_action_event_long_description': u'Valka is actively working to increase energy efficiency and the use of energy from renewable sources but such efforts also have adaptation\\u2013related benefits. One of  the most important activities involves complex energy saving measures for public educational institutions (Valka Music School, Valka Primary School and Valka Sport Hall) and apartment buildings. The energy efficiency and heat resistance measures implemented include insulating facades and roofs; replacing windows, doors, and floors; renewing heating systems; reconstructing lighting and electrical power systems; and installing ventilation systems. By renovating buildings, Valka is also improving their resistance to the impacts of extreme temperatures.',
    'f_m_action_event_title': 'Improving of the heat resistance of municipal buildings',
    'f_picture_caption': "Valka's renovated Sports Hall",
    'f_sectors_concerned': ['Financial', 'Energy', 'Urban'],
    'h_m_elements': 'Sector Policies',
    'image': '11288937'
    }
    """

    def map_titles_to_tokens(context, vocab_factory):
        from zope.schema.interfaces import IVocabularyFactory

        if IVocabularyFactory.providedBy(vocab_factory):
            vocab = vocab_factory(context)
            t2t_map = {t.title.lower(): t.token for t in vocab}
        else:
            t2t_map = {v.lower(): k for k, v in list(vocab_factory.items())}

        def t2tmap(values):
            tokens = []

            if isinstance(values, str):
                if values.lower() == 'select':
                    return tokens
                token = t2t_map.get(values.lower())

                if token:
                    return token
            else:
                for v in values:
                    token = t2t_map.get(v.lower())

                    if token:
                        tokens.append(token)

            return tokens

        return t2tmap

    mpttt = map_titles_to_tokens
    c = container
    map_climate_impacts = mpttt(c, aceitem_climateimpacts_vocabulary)
    map_country = mpttt(c, ace_countries_vocabulary)
    map_impacted_sectors = mpttt(c, aceitem_sectors_vocabulary)
    map_elements = mpttt(c, aceitem_elements_vocabulary)

    def map_to_x(x):
        return ""

    _map = {
        'a_m_city_latitude': {'newkey': 'city_latitude'},
        'a_m_city_longitude': {'newkey': 'city_longitude'},
        'a_m_country': {
            'newkey': 'country', 'mapping_fnc': map_country},
        'a_m_name_of_local_authority': {'newkey': 'name_of_local_authority'},
        'a_population_size': {'newkey': 'population_size'},
        'b_m_climate_impacts': {
            'newkey': 'climate_impacts_risks_particularly_for_city_region',
            'mapping_fnc': map_climate_impacts},
        'b_climate_impacts_additional_information': {
            'newkey': 'additional_information_on_climate_impacts'},
        'b_m_covenant_of_mayors_signatory': {
            'newkey': 'covenant_of_mayors_signatory',
            'mapping_fnc': lambda x: x and x.lower() == 'yes'},
        'b_m_name_surname_of_mayor': {'newkey': 'name_and_surname_of_mayor'},
        'b_m_official_email': {'newkey': 'official_email'},
        'b_m_sector': {
            'newkey': 'key_vulnerable_adaptation_sector',
            'mapping_fnc': map_impacted_sectors},
        'b_m_r_email_of_contact_person': {'newkey': 'e_mail_of_contact_person'},
        'b_m_r_name_surname_of_contact_person': {'newkey': 'name_and_surname_of_contact_person'},
        'b_m_role_of_contact_person': {'newkey': 'role_of_contact_person'},
        'b_m_telephone': {'newkey': 'telephone'},
        'b_m_website_of_the_local_authority': {'newkey': 'website_of_the_local_authority'},
        'b_signature_date': {
            'newkey': 'signature_date',
            'mapping_fnc': lambda x: dt.fromtimestamp(int(x) / 1e3).date()},
        'd_adaptation_strategy_date_of_approval': {
            'newkey': 'date_of_approval_of_the_strategy__plan',
            'mapping_fnc': lambda x: dt.fromtimestamp(int(x) / 1e3).date()},
        'd_adaptation_strategy_name': {'newkey': 'name_of_the_strategy__plan'},
        'd_adaptation_strategy_summary': {'newkey': 'short_content_summary_of_the_strategy__plan'},
        'd_adaptation_strategy_weblink': {'newkey': 'weblink_of_the_strategy__plan'},
        'd_m_developed_an_adaptationstrategy': {
            'newkey': 'have_you_already_developed_an_adaptation_strategy',
            'mapping_fnc': lambda x: map_to_x(x) or ""},
        'e_additional_information_on_adaptation_responses': {'newkey': 'additional_information_on_adaptation_responses'},
        'f_picture_caption': {'newkey': 'picture_caption', 'mapping_fnc': lambda x: t2r(x) or ""},
        'f_sectors_concerned': {
            'newkey': 'what_sectors_are_concerned',
            'mapping_fnc': map_impacted_sectors},
        'h_m_elements': {
            'newkey': 'adaptation_elements', 'mapping_fnc': map_elements},
        'e_m_motivation': {'newkey': 'main_motivation_for_taking_adaptation_action'},
        # 'b_city_background': {'newkey': 'city_background'},
        # 'b_sector_additional_information': {'newkey': 'sector_additional_information'},
        # XXX: this seems to be duplicated with d_adaptation_strategy_weblink
        # 'e_adaptation_weblink': {'newkey': 'developed_an_adaptationstrategy'},
        'e_m_planed_adaptation_actions': {'newkey': 'planned_current_adaptation_actions_and_responses'},
        'f_m_action_event_long_description': {'newkey': 'long_description', 'mapping_fnc': lambda x: t2r(x) or ""},
        'f_m_action_event_title': {'newkey': 'title_of_the_action_event'},
    }

    # missing_vals = []
    # for _type, name, payload in vals:
    #     if name not in _map:
    #         missing_vals.append((_type, name, payload))
    #
    # for v in missing_vals:
    #     print v

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

    if data.get('f_picture'):
        img = get_repofile_by_id(portal.get(), data['f_picture'])

        if img:
            mapped_data['picture'] = img.image

    _publish = journal.status == 0  # is this a published city?

    geoloc_lat = s2d(mapped_data.pop('city_latitude'))
    geoloc_long = s2d(mapped_data.pop('city_longitude'))

    # if geoloc_lat and geoloc_long:
        # geoloc = Geolocation(latitude=geoloc_lat, longitude=geoloc_long)
        # mapped_data['geolocation'] = geoloc

    city = createAndPublishContentInContainer(
        container,
        'eea.climateadapt.city_profile',
        id=journal.urltitle,
        _publish=_publish,
        **mapped_data
    )
    logger.debug("Imported city profile %s", city_name)

    return city


def import_city_profiles(site):
    template_pks = {}

    for data in session.query(sql.Ddmtemplate):
        name = strip_xml(data.name)
        template_pks[name] = data.templatekey

    _id = template_pks['City Profile']
    cp = defaultdict(lambda: [])
    query = session.query(sql.Journalarticle).filter_by(templateid=_id)

    for data in query:
        name = strip_xml(data.title)
        cp[name].append(data)

    to_import = []

    for city_name in cp:
        if city_name and city_name != '-':
            cities = cp[city_name]
            cities.sort(key=lambda d: d.version)
            to_import.append(cities[-1])

    if not 'city-profile' in site.contentIds():
        city_profiles_folder = createAndPublishContentInContainer(
            site,
            'Folder',
            id='city-profile',
            title='City Profiles',
        )
    city_profiles_folder = site['city-profile']
    imported = []
    to_import = sorted(to_import, key=lambda x: x.title)

    for data in to_import:
        obj = import_city_profile(city_profiles_folder, data)
        imported.append(obj)

    return imported


@log_call
def import_template_help(site, layout, structure):
    main_title = structure.pop('name')
    cover = create_cover_at(site, layout.friendlyurl,
                            title=strip_xml(main_title))
    cover.aq_parent.edit(title=main_title)  # Fix parent name
    stamp_cover(cover, layout)

    column_names = ['column-1', 'column-2', 'column-3', 'column-4', 'column-5']
    lrow = []

    img_1 = structure['column-2'][0][1]['content'][0]
    img_2 = structure['column-3'][0][1]['content'][0]
    img_3 = structure['column-4'][0][1]['content'][0]
    img_4 = structure['column-5'][0][1]['content'][0]
    img_5 = structure['column-1'][0][1]['content'][0]
    img_6 = structure['column-3'][1][1]['content'][0]
    img_7 = structure['column-4'][1][1]['content'][0]

    img_1 = img_1.replace("/documents/18/11284244/Glossary+of+terms.jpg",
                          "/++theme++climateadapt/static/cca/img/cca-glossary.jpg")
    img_2 = img_2.replace("/documents/18/11284244/Reproductor.jpg",
                          "/++theme++climateadapt/static/cca/img/cca-videos.jpg")
    img_3 = img_3.replace("/documents/18/11284244/FAQ.jpg",
                          "/++theme++climateadapt/static/cca/img/cca-faq.jpg")
    img_4 = img_4.replace("/documents/18/11284244/Share+information.jpg",
                          "/++theme++climateadapt/static/cca/img/Share information.jpg")
    img_5 = img_5.replace("/documents/18/11284244/Help.jpg",
                          "/++theme++climateadapt/static/cca/img/cca-main.jpg")
    img_6 = img_6.replace("/documents/18/11284244/ec_icon.jpg",
                          "/++theme++climateadapt/static/cca/img/ec_icon.jpg")
    img_7 = img_7.replace("/documents/18/11284244/eea_icon.jpg",
                          "/++theme++climateadapt/static/cca/img/eea_icon.jpg")

    structure['column-2'][0][1]['content'][0] = img_1
    structure['column-3'][0][1]['content'][0] = img_2
    structure['column-4'][0][1]['content'][0] = img_3
    structure['column-5'][0][1]['content'][0] = img_4
    structure['column-1'][0][1]['content'][0] = img_5
    structure['column-3'][1][1]['content'][0] = img_6
    structure['column-4'][1][1]['content'][0] = img_7

    main_tile = make_tile(cover, structure.pop('column-1'))

    for name in column_names:   # Try to preserve the order of columns
        col = structure.get(name)

        if col:
            # each column has two tiles
            tiles = [make_tile(cover, [p], no_titles=True) for p in col]
            group = make_group(3, *tiles)
            lrow.append(group)

    main_row = make_row(*[make_group(12, main_tile)])
    lower_row = make_row(*lrow)
    layout = make_layout(main_row, lower_row)

    layout = json.dumps(layout)
    cover.cover_layout = layout

    return cover


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

    assert (len(structure) >= 2)
    assert (len(structure['column-1']) == 1)
    assert (len(structure['column-2']) == 1)

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
                if isinstance(info, str):
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

    # image_tile = make_image_tile(site, cover, image_info)    # TODO: import image
    image = get_repofile_by_id(site, image_info['id'])
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
        # TODO: add these redirections:
        # /climate-change-adaptation => /en/adaptation-information/general
        # /en/adaptation-information/general => /adaptation-information/general
        # /vulnerability-assessment => same as above

        return

    assert (len(structure) == 5)
    assert (len(structure['column-1']) == 1)
    assert (len(structure['column-2']) == 1)
    assert (len(structure['column-3']) == 1)
    assert (len(structure['column-4']) == 1)

    name = structure['name']
    cover = create_cover_at(site, layout.friendlyurl, title=str(name))
    stamp_cover(cover, layout)

    main = {}

    title = structure['column-1'][0][1]['content'][1][2][0]
    body = structure['column-1'][0][1]['content'][2][2][0]
    readmore = structure['column-1'][0][1]['content'][3][2][0]
    image_id = structure['column-1'][0][1]['content'][0][2][0]
    image = get_repofile_by_id(site, image_id)

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
                                                   'text': main_content,
                                                   'css_class': 'clearfix'})

    col2_tile = make_tile(cover, structure['column-2'], 'col-md-4')
    col3_tile = make_tile(cover, structure['column-3'], 'col-md-8')

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

    assert (len(structure) == 3)
    assert (len(structure['column-1']) == 1)

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

    if name == 'Urban areas':
        name = str(col1[0][1]['content'][1][2][0])

    cover = create_cover_at(site, layout.friendlyurl, title=name)
    stamp_cover(cover, layout)
    cover.aq_parent.edit(title=main['title'])    # Fix cover's parent title

    if layout.themeid == "balticseaace_WAR_acetheme":
        # TODO: mark the content with a special interface to enable the menu
        alsoProvides(cover, IBalticRegionMarker)

    main['image'].update({'title': '', 'thumb': ''})

    if main['image']['id']:
        image = get_repofile_by_id(site, main['image']['id'])

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

    # sidebar_tile = make_aceitem_search_tile(cover, sidebar[0][1])
    sidebar_tiles = make_tiles(cover, sidebar)

    sidebar_group = make_group(3, *sidebar_tiles)
    main_content_group = make_group(9,
                                    main_content_tile, *relevant_content_tiles)
    layout = make_layout(make_row(main_content_group, sidebar_group))
    cover.cover_layout = json.dumps(layout)
    cover._p_changed = True

    return cover


@log_call
def import_template_ace_layout_4(site, layout, structure):
    # done, parent title fixed

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
        'Results': 'Expected results',
        'ProjectPartners': 'Project partners',
        'Deliverables': 'Deliverables',
    }
    partners = []

    for line in structure['column-1'][0][1]['content']:
        if line[0] == 'image':
            if line[2] == None:
                logger.info("Skipping empty layout %s", layout.friendlyurl)
                # these are empty projects

                return
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

    _sidebar = []
    _contact = []
    _website = None

    for dyn, name, payload in _main_sidebar:
        if name == "ProjectWebSite":
            _website = payload[0]

            continue

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

    if _website and (not _website.startswith('http')):
        _website = 'http://' + _website
    _contact.append(('ProjectWebSite', _website))

    contact_text = render("templates/snippet_contact.pt", {'lines': _contact,
                                                           'labels': labels})
    _sidebar.append(('ContactPoint', contact_text))
    sidebar_text = render("templates/snippet_sidebar_text.pt",
                          {'lines': _sidebar, 'labels': labels})
    sidebar_tile = make_richtext_with_title_tile(
        cover, {'title': sidebar_title, 'text': sidebar_text})

    lu_tile = make_view_tile(cover, {'view_name': 'view_last_modified'})

    sidebar_tiles = [sidebar_tile, lu_tile]

    if len(structure['column-2']) > 1:
        for pid, portlet in structure['column-2'][1:]:
            tile = make_richtext_with_title_tile(
                cover, {'title': portlet['portlet_title'],
                        'text': portlet['content'][0]})
            sidebar_tiles.append(tile)

    # the accordion is a list of ('tab title', 'tab content structure')
    # we need to go through each of the tabs and change the structure to be html

    payload = []
    # import pdb; pdb.set_trace()

    for k, v in main['accordion']:
        # TODO: get the keys from dictionary

        if not k == 'Project Partners':
            payload.append((k, v))
        else:
            table = {'rows': v, 'cols': []}
            payload.append((k, render('templates/table.pt', table)))

    image = get_repofile_by_id(site, main['image'])
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

    #  u'column-2': [(u'astheaderportlet_WAR_ASTHeaderportlet_INSTANCE_AQlGpTEbY3Eg',
    #                 {'headertext': u'Implementation',
    #                  'portletSetupCss': u'{"wapData":{"title":"","initialWindowState":"NORMAL"},"spacingData":{"margin":{"sameForAll":true,"bottom":{"unit":"px","value":""},"left":{"unit":"px","value":""},"right":{"unit":"px","value":""},"top":{"unit":"px","value":""}},"padding":{"sameForAll":true,"bottom":{"unit":"px","value":""},"left":{"unit":"px","value":""},"right":{"unit":"px","value":""},"top":{"unit":"px","value":""}}},"borderData":{"borderStyle":{"sameForAll":true,"bottom":"","left":"","right":"","top":""},"borderColor":{"sameForAll":true,"bottom":"","left":"","right":"","top":""},"borderWidth":{"sameForAll":true,"bottom":{"unit":"px","value":""},"left":{"unit":"px","value":""},"right":{"unit":"px","value":""},"top":{"unit":"px","value":""}}},"textData":{"fontWeight":"","lineHeight":"","textDecoration":"","letterSpacing":"","color":"","textAlign":"","fontStyle":"","fontFamily":"","wordSpacing":"","fontSize":""},"bgData":{"backgroundPosition":{"left":{"unit":"px","value":""},"top":{"unit":"px","value":""}},"backgroundColor":"","backgroundRepeat":"","backgroundImage":"","useBgImage":false},"advancedData":{"customCSS":"","customCSSClassName":""}}',
    #                  'portletSetupShowBorders': u'false',
    #                  'portletSetupUseCustomTitle': u'false',
    #                  'step': u'5'}),

    assert (len(structure) >= 3)
    assert (len(structure['column-1']) == 1)
    assert (len(structure['column-2']) >= 2)

    section_title = structure['column-2'][1][1]['portlet_title']

    if structure['name'] == 'Urban AST step 0-0':
        section_title = structure['name']

    cover = create_cover_at(site, layout.friendlyurl, title=section_title)
    cover.aq_parent.edit(title=structure['name'])   # Fix parent name
    stamp_cover(cover, layout)

    imgp = structure['column-1'][0][1]['content'][0]
    imgp = imgp.replace("/ace-theme/css/", "/++theme++climateadapt/static/")
    imgp = imgp.replace("/ace-theme/js/",  "/++theme++climateadapt/static/")
    imgp = imgp.replace("jquery.qtip.min.css", "jquery.qtip.css")

    image_tile = make_richtext_tile(cover, {'text': imgp,
                                            'title': 'AST Image'})
    nav_tile = nav_tile_maker(cover)
    side_group = make_group(4, image_tile, nav_tile)

    main_section_title = structure['column-2'][0][1]['headertext']
    step = structure['column-2'][0][1]['step']

    # column-2 is full width tiles
    main_content_tiles = make_tiles(cover, structure['column-2'],
                                    css_class='padded-tile')

    # create tiles in the remaining columns
    [structure.pop(z) for z in ['column-1', 'column-2', 'name']]

    if structure:
        second_row_group = []

        for name in sorted(structure.keys()):
            column = structure[name]
            tiles = []

            for tile in column:
                tile = make_tile(cover, [tile])
                tiles.append(tile)
            group = make_group(6, *tiles)
            second_row_group.append(group)
        second_row = make_row(*second_row_group)
        main_content_tiles.append(second_row)

    if is_urbanast:
        tile = make_view_tile(cover,
                              {'title': 'UrbanAST nav',
                               'view_name': 'urbanast_bottom_nav'})
        third_row = make_group(8, tile)
        main_content_tiles.append(third_row)

    main_group = make_group(8, *main_content_tiles)

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
    logger.error("Please investigate this importer %s with template %s",
                 layout.friendlyurl, '1_2_columns_i')
    raise ValueError

    return


@log_call
def import_template_1_2_columns_ii(site, layout, structure):
    # done, parent title fixed

    # ex page: /share-your-info/general

    # row 1: text + image
    # row 2: share button

    assert (len(structure) == 2 or len(structure) == 3)
    assert (len(structure['column-1']) == 1)

    if len(structure) > 2:
        assert (len(structure['column-2']) == 1)

    content_portlet = structure['column-1'][0][1]['content']

    for bit in content_portlet:
        if bit[0] == 'image':
            image = bit[-1]

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

    cover.cover_layout = json.dumps(_make_share_page_layout(
        site, cover, structure, title, body, image, share_portlet_title,
        share_portlet
    ))

    return cover


def _make_share_page_layout(site, cover, structure, title, body, image,
                            share_portlet_title, share_portlet):

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

    return layout


@log_call
def import_template_1_column(site, layout, structure):
    # done, fixed parent title
    # this is a simple page, with one portlet of text
    # example: /eu-adaptation-policy/funding/life
    # import pdb; pdb.set_trace()

    if layout.friendlyurl == '/share-your-info':
        img_1 = structure['column-1'][0][1]['content'][0]
        img_1 = img_1.replace("/documents/18/11284244/FAQ.jpg",
                              "/++theme++climateadapt/static/cca/img/cca-faq.jpg")
        structure['column-1'][0][1]['content'][0] = img_1

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

    cover_title = str(structure['name'])

    # detect /transnational-regions pages
    def is_transnational_region():
        if not ('column-1' in structure):
            return False

        if not ('content' in structure['column-1'][0][1]):
            return False
        content = structure['column-1'][0][1]['content']
        names = [x[1] for x in content]

        if 'region_name' in names:
            return True

    if is_transnational_region():
        return _import_transnational_region_page(site, layout, structure)

    # try to get the main title and set it on the parent folder
    portlet_title = structure['column-1'][0][1].get('portlet_title')

    if portlet_title:
        main_title = portlet_title
    else:
        main_title = structure['column-1'][0][1].get('title') or ""
    main_title = strip_xml(main_title) or cover_title

    if portlet_title == 'Network':
        cover_title = 'Network'

    cover = create_cover_at(site, layout.friendlyurl, title=cover_title)
    cover.aq_parent.edit(title=main_title)  # Fix parent title

    if layout.friendlyurl in additional_sharepage_layouts:
        alsoProvides(cover, IClimateAdaptSharePage)
    stamp_cover(cover, layout)

    def _import_two_columns():
        content = structure['column-1'][0][1].get('content')

        col1 = "".join(content)
        col2 = "".join(structure['column-1'][1][1]['content'][0])

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
            # these are the /share-your-info/indicators pages
            # layout is similar to 1_2_columns_ii
            # [('image', 'Image', ['11285089']),
            # ('dynamic', 'Title', ['Map Graph Data']),
            #  ('text',
            #     'Body',
            #     [u'<p><br />\n<strong>Definition: </strong><br />\nMap Graph Data ....</p>\n\n<p>In this section of CLIMATE-ADAPT, map graph data is included at EU level (e.g. from the European Commission) or from countries.</p>\n\n<p>Governmental organisations are expected to provide proposals for this type of content.</p>\n\n<p>See an <a href="/viewaceitem?aceitem_id=3660">example</a> of a CLIMATE-ADAPT map graph data.</p>'])]
            # this is a dynamic portlet

            for bit in content:
                if bit[0] == 'image':
                    image = bit[-1][0]

                if bit[0] == 'text':
                    body = bit[-1][0]

                if bit[0] == 'dynamic' and bit[1] == 'Title':
                    title = bit[-1][0]
            share_portlet_title = title
            share_portlet = structure['column-1'][1][1]
            layout = _make_share_page_layout(
                site, cover, structure, title, body, image, share_portlet_title,
                share_portlet
            )

            return layout

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

    if layout.friendlyurl == '/tools/urban-ast/contact':
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

    assert (len(structure) in [2, 3])

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

    if layout.friendlyurl in ['/observations-and-scenarios',
                              '/adaptation-measures',
                              '/adaptation-support-tool']:

        return  # this is imported in another layout

    if len(structure) == 1:  # this is a fake page. Ex: /adaptation-sectors
        logger.error("Please investigate this importer %s with template %s",
                     layout.friendlyurl, '2_columns_ii')
        raise ValueError

    if layout.friendlyurl == '/mayors-adapt/register':
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

    assert (len(structure) == 2 or len(structure) == 3)

    # title = structure['name']
    title = structure['column-1'][0][1]['portlet_title']

    if not title:
        title = structure['name']
    body = structure['column-1'][0][1]['content'][0]

    cover = create_cover_at(site, layout.friendlyurl, title=title)
    cover.aq_parent.edit(title=title)   # Fix parent title
    stamp_cover(cover, layout)

    # there are three pages that use dynamic text (faq items)
    portlet_types = [x[0] for x in structure['column-1'][0][1]['content']]
    portlet_names = [x[1] for x in structure['column-1'][0][1]['content']]

    if 'dynamic' in portlet_types:
        # a page with readmore structure

        if 'Body' in portlet_names and 'ReadMoreBody' in portlet_names:

            main = {}

            for _type, name, payload in structure['column-1'][0][1]['content']:
                if _type == 'image':
                    if isinstance(payload, str):
                        image_id = payload
                    else:
                        image_id = payload[0]

                    image = get_repofile_by_id(site, image_id)

                if _type == 'dynamic' and name == 'Title':
                    if isinstance(payload, str):
                        title = payload
                    else:
                        title = payload[0]

                if _type == 'text':
                    if name == 'Body':
                        body = payload[0]

                    if name == 'ReadMoreBody':
                        readmore = payload[0]

            # image_id = structure['column-1'][0][1]['content'][0][2][0]
            # image = get_repofile_by_id(site, image_id)
            # title = structure['column-1'][0][1]['content'][1][2][0]
            # body = structure['column-1'][0][1]['content'][2][2][0]
            # readmore = structure['column-1'][0][1]['content'][3][2][0]

            main['title'] = title
            main['body'] = body
            main['readmore'] = readmore

            main['image'] = {
                'title': image.Title(),
                'thumb': localize(image, site) + "/@@images/image",
            }

            # Fix cover parent title
            cover.aq_parent.edit(title=main['title'])

            main_content = render(
                'templates/richtext_readmore_and_image.pt', {'payload': main})

            main_content_tile = make_richtext_with_title_tile(
                cover, {'text': main_content, 'title': ''})

            sidebar_tiles = make_tiles(cover, structure['column-2'])
            sidebar_group = make_group(3, *sidebar_tiles)
            main_content_group = make_group(9, main_content_tile)
            layout = make_layout(make_row(main_content_group, sidebar_group))
            layout = json.dumps(layout)

            cover.cover_layout = layout
            cover.setLayout('standard')

            return cover

        else:
            htmlstring = ''

            for row in structure['column-1'][0][1]['content']:
                row_type = row[0]

                if row_type == 'text':
                    htmlstring += row[2][0]
                elif row_type == 'dynamic':
                    question = row[2][0][2][0]
                    newquestion = '<p class="ugquestion">' + question + '</p>'
                    answer = row[2][1][2][0]
                    htmlstring += newquestion + answer
            main_content_tile = make_richtext_with_title_tile(
                cover, {'text': htmlstring, 'title': ''})

        side_group = make_group(5)
        main_group = make_group(7, main_content_tile)
        layout = make_layout(make_row(main_group, side_group))

        cover.cover_layout = json.dumps(layout)
        cover.setLayout('standard')

        return cover

    extra_tiles = []

    if len(structure['column-1']) == 4:
        # There is only one layout with this structure
        # TODO: do this page, it's the /organisations page
        # filter_portlet_1 = structure['column-1'][1]
        # filter_portlet_2 = structure['column-1'][2]
        # blue_button = structure['column-1'][3][1]['content'][0]
        extra_tiles = [make_tile(cover, [p])
                       for p in structure['column-1'][1:]]
    elif len(structure['column-1']) == 2:
        body += structure['column-1'][1][1]['content'][0]

    image = None

    if len(structure) == 3:
        # column-2 has a image
        assert (len(structure['column-2']) == 1)
        image = structure['column-2'][0][1]['content'][0]

    # Fix images

    if image is not None:
        image = image.replace("/documents/18/0/",
                              "/++theme++climateadapt/static/cca/img/")

    # title = structure['name']
    title = ''

    main_content_tile = make_richtext_with_title_tile(cover,
                                                      {'text': body, 'title': title})

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

    logger.error("Please investigate this importer %s with template %s",
                 layout.friendlyurl, 'ace_layout_1')
    raise ValueError


@log_call
def import_template_ace_layout_5(site, layout, structure):
    # done, fixed parent title
    # ex page: /transnational-regions/caribbean-area
    # 1 row, 2 columns. First column: image + region selection tile
    #                   Second column: rich text
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
            main_text += "<h3>{0}</h3>\n{1}".format(title, text)
    else:
        main_text = texts[0]

    cover = create_cover_at(site, layout.friendlyurl,
                            title=title or main_title)
    cover.aq_parent.edit(title=main_title)
    alsoProvides(cover.aq_parent, ITransnationalRegionMarker)
    cover.aq_parent.reindexObject(idxs=('object_provides',))

    main_info = {'title': main_title, 'text': main_text}
    image_info = {
        'id': image,
        'description': '',
        'title': 'region image',
    }

    main_text_tile = make_richtext_with_title_tile(cover, main_info)
    dropdown_tile = make_transregion_dropdown_tile(cover)
    image_tile = make_image_tile(
        site, cover, image_info)    # TODO: import image

    image_group = make_group(3, image_tile, dropdown_tile)
    main_text_group = make_group(9, main_text_tile)

    row_1 = make_row(image_group, main_text_group)
    layout = make_layout(row_1)
    cover.cover_layout = json.dumps(layout)

    return cover


def _import_transnational_region_page(site, layout, structure):
    # ex page: /transnational-regions/balkan-mediterranean
    # 1 row, 2 columns:
    # first column, 2 tiles: image, region selector
    # second column: 1 tile, rich text

    _titles = {
        'policy_framework': "Policy framework",
        'assessments_and_projects': "Assessments and projects",
        'assessments_and_projects_': "Assessments and projects",
        'Detailed_Information': "Detailed information",
    }
    # import pdb; pdb.set_trace()

    _info = {}
    _info['title'] = ''
    _info['countries'] = []

    content = structure['column-1'][0][1]['content']
    _info['main_text'] = ''

    for _type, name, payload in content:
        if name == 'region_name':
            _info['title'] = payload[0]

        if _type == 'image':
            _info['image'] = payload[0]

            continue

        if name == 'link_to_country':
            # [('dynamic', 'link_to_country_desc', ['Bulgaria']),
            #                                       '/countries/Bulgaria']
            country_name = payload[0][2][0]
            country_link = payload[1]
            _info['countries'].append((country_name, country_link))

        if _type == 'text':
            if len(payload) > 1:
                for bit in payload:
                    title = _titles[bit[1]]
                    text = bit[2][0]
                    _info['main_text'] += "<h3>{0}</h3>\n{1}".format(
                        title, text)
            else:
                text = payload[0]
                title = _titles[name]
                _info['main_text'] += "<h3>{0}</h3>\n{1}".format(
                    title, text)

    cover = create_cover_at(site, layout.friendlyurl, title=_info['title'])
    alsoProvides(cover.aq_parent, ITransnationalRegionMarker)
    cover.aq_parent.reindexObject(idxs=('object_provides',))
    cover.aq_parent.edit(title=_info['title'])

    main_info = {'title': _info['title'], 'text': _info['main_text']}
    image_info = {
        'id': _info['image'],
        'description': '',
        'title': 'region image',
    }
    region_name = _info['title'].replace(' Area', '').\
        replace(' Region', '').strip()

    main_text_tile = make_richtext_with_title_tile(cover, main_info)

    image_tile = make_image_tile(
        site, cover, image_info)    # TODO: import image
    dropdown_tile = make_transregion_dropdown_tile(cover,
                                                   {'region': region_name})

    main_text_group = make_group(10, main_text_tile)
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

    # done, parent title fixed
    # TODO: fix styling of columns
    # TODO: fix images path

    assert (len(structure) == 5)
    assert (len(structure['column-1']) == 1)
    assert (len(structure['column-2']) == 1)
    assert (len(structure['column-3']) == 1)
    assert (len(structure['column-4']) == 1)

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


def import_journal_articles(site):

    parent = create_folder_at(site, '/more-events')
    # create_plone_content(
    #     parent,
    #     type='Collection',
    #     title='Events',
    #     slug='events',
    #     sort_on=u'effective',
    #     sort_reversed=True,
    #     query=[{u'i': u'portal_type',
    #             u'o': u'plone.app.querystring.operation.selection.is',
    #             u'v': [u'Event']},
    #            {u'i': u'path',
    #             u'o': u'plone.app.querystring.operation.string.relativePath',
    #             u'v': u'..'}],)
    # parent.setDefaultPage('events')
    parent.edit(title="More Events")
    parent.setLayout('event_listing')

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
            date = dateutil.parser.parse(
                "{0} {1} {2}".format(day, month, year))
            date = utc.localize(date)

            event = create_plone_content(parent, type='Event', id=slug,
                                         title=title, location=location,
                                         start=date, end=date, whole_day=True,
                                         timezone='UTC',
                                         event_url=link, effective_date=publish_date)

            logger.debug("Created Event at %s with effective %s" %
                         (event.absolute_url(), str(publish_date)))
        else:
            print("no structure id")
            import pdb
            pdb.set_trace()

    parent = create_folder_at(site, '/news-archive')
    parent.edit(title="News Archive")
    create_plone_content(
        parent,
        type='Collection',
        title='News',
        slug='news',
        sort_on='effective',
        sort_reversed=True,
        query=[{'i': 'portal_type',
                'o': 'plone.app.querystring.operation.selection.is',
                'v': ['News Item']},
               {'i': 'path',
                'o': 'plone.app.querystring.operation.string.relativePath',
                'v': '..'}],)
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
            # link_title = attrs['title']
            news = create_plone_content(parent, type='Link', id=slug,
                                        title=title, remoteUrl=link,
                                        effective_date=publish_date)
            logger.debug("Created Link for news at %s with effective %s" %
                         (news.absolute_url(), publish_date))
        else:
            try:
                text = t2r(content[0])
            except Exception:   # TODO: there's a news item that's actually an event, that's actually a Link
                continue
            news = create_plone_content(parent, type='News Item', id=slug,
                                        title=title, text=text,
                                        effective_date=publish_date)
            logger.debug("Created News Item for news at %s",
                         news.absolute_url())


def get_default_location(site, _type):
    """ Returns the proper folder for a database item to be created.

    If the folder doesn't exist, it creates it and adds the proper roles to it.
    """

    path, title, factory = DEFAULT_LOCATIONS[_type]
    dbname, name = path.split('/')

    parent = site

    if not dbname in site.contentIds():
        parent = createAndPublishContentInContainer(
            site,
            'Folder',
            id=dbname,
            title='Database',
        )
    else:
        parent = site._getOb(dbname)

    if name in parent.contentIds():
        dest = parent._getOb(name)
    else:
        dest = createAndPublishContentInContainer(
            parent,
            'Folder',
            id=name,
            title=title,
        )
        roles = dest.__ac_local_roles__
        roles.update(AuthenticatedUsers=['Contributor', 'Reader'])
        # roles.update(ContentReviewers=[u'Contributor', u'Reviewer', u'Editor',
        #                                u'Reader'])
        roles.update({'extranet-cca-powerusers':
                      ['Contributor', 'Editor', 'Reader']})
        dest.immediately_addable_types = [factory]
        dest.locally_allowed_types = [factory]
        dest.constrain_types_mode = 1
        dest.manage_addProperty('search_type_name', _type, 'string')
        dest.setLayout('@@redirect_to_search_page')

    return dest


def import_aceitems(session, site):
    for aceitem in session.query(sql.AceAceitem):
        if aceitem.datatype in ['ACTION', 'MEASURE', "RESEARCHPROJECT",
                                "MEASURE", "ACTION"]:

            continue
        import_aceitem(aceitem, get_default_location(site, aceitem.datatype))

    for aceproject in session.query(sql.AceProject):
        import_aceproject(aceproject, get_default_location(site,
                                                           'RESEARCHPROJECT'))

    # first import the adaptation options, then the case studies
    # because case studies have references to adaptation options
    q = session.query(sql.AceMeasure)

    for acemeasure in q.filter(sql.AceMeasure.mao_type != 'A'):
        import_adaptationoption(acemeasure, get_default_location(site,
                                                                 'MEASURE'))

    for acemeasure in q.filter(sql.AceMeasure.mao_type == 'A'):
        import_casestudy(acemeasure, get_default_location(site, 'ACTION'))

    fix_casestudy_images(site)


def _fix_casestudy_images(casestudy):
    # set the primephoto as uploaded field to primary_photo
    # move the supphotos inside the case study

    for rel in casestudy.supphotos:
        img = rel.to_object
        move(img, casestudy)
        logger.info("Move photo %s inside casestudy, %s",
                    img.absolute_url(),
                    casestudy.absolute_url())

    casestudy.supphotos = []

    if casestudy.primephoto:
        img = casestudy.primephoto.to_object
        casestudy.primary_photo = img.image
        # TODO: remove the rel image
        logger.info("Changed primary photo of casestudy, %s",
                    casestudy.absolute_url())

    casestudy._p_changed = True


def fix_casestudy_images(site):

    # now we fix the images for the case studies
    catalog = getToolByName(site, 'portal_catalog')
    brains = catalog.searchResults(portal_type='eea.climateadapt.casestudy')

    for brain in brains:
        obj = brain.getObject()
        _fix_casestudy_images(obj)


def _fix_supdocs(obj):
    if obj.relatedItems:
        for rel in obj.relatedItems:
            t = rel.to_object
            move(t, obj)
            logger.info("Move file %s inside obj, %s", t.absolute_url(),
                        obj.absolute_url())
        obj.relatedItems = []
        obj._p_changed = True


def run_importer(site=None):
    sql.Address = sql.Addres    # wrong detected plural
    fix_relations(session)

    if 'dbshell' in sys.argv:
        import pdb
        pdb.set_trace()

    if site is None:
        site = get_plone_site()

    wftool = getToolByName(site, "portal_workflow")

    structure = [('repository', 'Repository')]

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

    import_aceitems(session, site)

    for layout in session.query(sql.Layout).filter_by(privatelayout=False):
        try:
            cover = import_layout(layout, site)
        except Exception:
            logger.exception("Couldn't import layout %s", layout.friendlyurl)

        if cover:
            cover._imported_comment = \
                "Imported from layout {0} - {1}".format(layout.layoutid,
                                                        layout.uuid_)
            logger.debug("Created cover at %s", cover.absolute_url())

    import_journal_articles(site)
    import_city_profiles(site)

    tweak_site(site)
    write_links()


def tweak_site(site):
    """ Apply any other tweaks to the site
    """

    acl_users = site._getOb('acl_users')
    # acl_users.manage_addProduct['PlonePAS'].manage_addAutoGroup(
    #     id='members_auto_group', title='Members AutoGroup', group='Members',
    #     description="Set Members group for everybody logged in")

    acl_users.manage_addProduct['eea.climateadapt'].\
        manage_addCityMayorUserFactory(id="city_mayor_user_plugin",
                                       title="CityMayor Users Plugin")
    plugin_obj = acl_users._getOb('city_mayor_user_plugin')

    ifaces = ['IAnonymousUserFactoryPlugin', 'IUserEnumerationPlugin']
    plugin_obj.manage_activateInterfaces(ifaces)

    ast_tools = ['tools/urban-ast',
                 'adaptation-support-tool']

    for path in ast_tools:
        obj = site.restrictedTraverse(path)

        if not IASTNavigationRoot.providedBy(obj):
            alsoProvides(obj, IASTNavigationRoot)

    faceted_pages = [
        ('/data-and-downloads', 'search.xml', 'faceted-climate-listing-view'),
        ('/admin', 'admin.xml', None),
    ]

    for location, xmlfilename, layout in faceted_pages:
        # TODO: also add a title
        make_faceted(site, location, xmlfilename, layout)

    # reorder providedBy for '/data-and-downloads'

    dad = site['data-and-downloads']
    dad.title = 'Search the database'
    noLongerProvides(dad, IFacetedNavigable)
    alsoProvides(dad, ISiteSearchFacetedView)
    faceted_view = getMultiAdapter(
        (dad, site.REQUEST), name="faceted_subtyper")
    faceted_view.enable()
    IFacetedLayout(dad).update_layout('faceted-climate-listing-view')

    # countries page
    ctpage = site['countries']
    alsoProvides(ctpage, ICountriesRoot)
    ctpage.manage_changeProperties({'title': 'Country Information'})
    ctpage.setLayout('@@countries-view-map')

    # mayors-adapt page
    mapage = site['mayors-adapt']
    alsoProvides(mapage, IMayorAdaptRoot)
    mapage.manage_changeProperties({'title': 'Mayors Adapt'})
    mapage.setLayout('@@mayors-adapt')

    # city-profile page
    cities = site['city-profile']
    cities.setLayout('@@cities-listing')
    cities.immediately_addable_types = ['eea.climateadapt.city_profile']
    cities.locally_allowed_types = ['eea.climateadapt.city_profile']
    cities.constrain_types_mode = 1

    cities._Add_portal_content_Permission = ('CityMayor', 'Manager',
                                             'Contributor')
    cities._p_changed = True

    # content page
    contentpage = site['metadata']
    contentpage.setLayout('@@redirect_to_search_page')

    # transnational regions page
    trans_reg_page = site['transnational-regions']
    alsoProvides(trans_reg_page, ITransRegioRoot)
    trans_reg_page.manage_changeProperties({'title': 'Transnational regions'})
    trans_reg_page.setLayout('@@transnational-regions-view')

    # fix pages title
    titles = [
        ('project', 'Projects'),
        ('tools', 'Tools'),
        ('tools/general', 'General'),
        ('tools/urban-ast', 'Urban adaptation support tool'),
        ('tools/urban-ast', 'Urban adaptation support tool'),
        ('tools/urban-adaptation', 'Urban vulnerability Map book'),
        ('tools/urban-adaptation/introduction', 'Introduction'),
        ('tools/urban-adaptation/climatic-threats', 'Climatic threats'),
        ('tools/urban-adaptation/generic-response', 'Generic response'),
        ('tools/urban-adaptation/overview', 'Overview'),
        ('adaptation-information', 'Adaptation Information'),
        ('adaptation-information/general', 'General'),
    ]

    for path, title in titles:
        obj = site.restrictedTraverse(path)
        obj.edit(title=title)

    # set permitted addable content in various locations
    site['news-archive'].immediately_addable_types = ['News Item']
    site['news-archive'].locally_allowed_types = ['News Item', 'Image', 'File']
    site['news-archive'].constrain_types_mode = 1

    site['more-events'].immediately_addable_types = ['Event']
    site['more-events'].locally_allowed_types = ['Event', 'Image', 'File']
    site['more-events'].constrain_types_mode = 1

    # set permissions
    # {'extranet-cca-managers': [u'Contributor', u'Reviewer', u'Editor', u'Reader']}
    site.__ac_local_roles__.update({'extranet-cca-managers': ['Manager'],
                                    'extranet-cca-editors': ['Contributor'],
                                    'extranet-cca-checkers': ['Reader'],
                                    'extranet-cca-reviewers': ['Reviewer'],
                                    })
    site._p_changed = True

    # Explanation of roles from Prosperini:
    # cca-editors: former writer role (can add content and submit it for approval)
    #              they can check out web content
    # cca-reviewers: content reviewers everywhere
    # cca-checker: nothing, just a group for users that need to see unpublish
    #              content before it's published.

    site['more-events'].__ac_local_roles__.update(
        {'extranet-cca-newsevents': ['Contributor', 'Reviewer', 'Editor']})
    site['news-archive'].__ac_local_roles__.update(
        {'extranet-cca-newsevents': ['Contributor', 'Reviewer', 'Editor']})
    site['city-profile'].__ac_local_roles__.update(
        {'extranet-cca-ma-managers': ['Contributor', 'Reviewer', 'Editor']})

    _content = """
    <div class="asset-abstract ">
    <h3 class="asset-title"><a href="countries" data-linktype="external" data-val="/countries">Country information page</a></h3>
    <div class="asset-content">
    <div class="asset-summary">EEA Member countries are at different stages of preparing, developing and implementing national adaptation strategies and plans. See in the map below the information provided...</div>
    <div class="asset-more"><a href="countries" data-linktype="external" data-val="/countries">Read More</a></div>
    </div>
    <div class="asset-metadata"></div>
    </div>
    <div class="asset-abstract ">
    <h3 class="asset-title"></h3>
    <h3 class="asset-title"><a href="mayors-adapt" data-linktype="external" data-val="/mayors-adapt">Mayors Adapt landing page</a></h3>
    <div class="asset-content">
    <div class="asset-summary">Register your City Mayors Adapt - the Covenant of Mayors Initiative on Climate Change Adaptation has been set up by the European Commission to engage cities in...</div>
    <div class="asset-more"><a href="mayors-adapt" data-linktype="external" data-val="/mayors-adapt">Read More</a></div>
    </div>
    </div>
    """
    createAndPublishContentInContainer(
        site,
        'Document',
        title='More latest updates',
        text=t2r(_content)
    )


def get_plone_site():
    import Zope2
    app = Zope2.app()
    from Testing.ZopeTestCase.utils import makerequest
    app = makerequest(app)
    app.REQUEST['PARENTS'] = [app]
    from zope.globalrequest import setRequest
    setRequest(app.REQUEST)
    from AccessControl.SecurityManagement import newSecurityManager
    from AccessControl.SpecialUsers import system as user
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
