from collections import defaultdict
from eea.climateadapt._importer import sqlschema as sql
from eea.climateadapt._importer.utils import parse_settings, s2l, printe
from eea.climateadapt._importer.utils import SOLVERS
from eea.climateadapt._importer.utils import strip_xml
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from sqlalchemy import Column, BigInteger, String, Text, DateTime   #, text
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from zope.sqlalchemy import register
import logging
import lxml.etree
import os
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

PUBLICATION_REPORT = 'DOCUMENT'
INFORMATION_PORTAL = 'INFORMATIONSOURCE'
GUIDANCE_DOCUMENT = 'GUIDANCE'
TOOL = 'TOOL'
ORGINIZATION = 'ORGINIZATION'
ACE_ITEM_TYPES = {
    PUBLICATION_REPORT: 'eea.climateadapt.publicationreport',
    INFORMATION_PORTAL: 'eea.climateadapt.informationportal',
    GUIDANCE_DOCUMENT: 'eea.climateadapt.guidancedocument',
    TOOL: 'eea.climateadapt.tool',
    ORGINIZATION: 'eea.climateadapt.organization'
}


def noop(*args, **kwargs):
    """ no-op function to help with development of importers.
    It avoids pyflakes errors about not used variables.
    """
    return


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
                    item, item.aceitemid)
        return item


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
                item, item.aceitemid)

    return item


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
                item, item.aceitemid)

    return item


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
                item, item.measureid)

    return item


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
        articleid=articleid).order_by(
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

    article = _get_article_for_portlet(portlet)
    # if layout.friendlyurl == "/adaptation-support-tool/step-1/communicate-raise-awareness/terminology":
    #     import pdb; pdb.set_trace()
    if article is not None:
        e = lxml.etree.fromstring(article.content.encode('utf-8'))

        # TODO: attach other needed metadata
        return {'title': article.title,
                'description': article.description,
                'content': [SOLVERS[child.tag](child) for child in e]
                }

    logger.debug("Could not get an article from portlet %s for %s",
                    portletid, layout.friendlyurl)

    # extract portlet settings, must be an application's settings
    e = lxml.etree.fromstring(portlet.preferences)
    out = {}
    for pref in e.xpath('//preference'):
        name = pref.find('name').text
        value = pref.find('value')
        try:
            value = value.text
        except Exception:
            pass
        out[name] = value

    return out


def import_layout(layout, site):
    # import layout as folder
    # create documents for each portlet in 'typesettings':
    # u'sitemap-changefreq=daily\nlayout-template-id=2_columns_iii\nsitemap-include=1\ncolumn-2=56_INSTANCE_9tMz,\ncolumn-1=56_INSTANCE_2cAx,56_INSTANCE_TN6e,\n'
    # split content from layout template
    # search for portlet name in portletpreferences
    # parse the prefs and look for articleid
    # create page from journalarticle

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
    if importer:
        importer(layout, structure)
    else:
        logger.warning("No importer for template %s", template)


# possible templates are
# [u'1_2_1_columns', u'1_2_columns_i', u'1_2_columns_ii', u'1_column',
# u'2_columns_i', u'2_columns_ii', u'2_columns_iii', u'ace_layout_1',
# u'ace_layout_2', u'ace_layout_3', u'ace_layout_4', u'ace_layout_5',
# u'ace_layout_col_1_2', u'ast', u'faq', u'frontpage', u'transnationalregion',
# u'urban_ast']


def import_template_1_2_1_columns(layout, structure):
    # column-1 has a table with links and a table with info
    # column-2 has an iframe
    column1_content = structure['column-1'][0]
    column2_content = structure['column-2'][0]

    # import pdb; pdb.set_trace( )


def import_template_transnationalregion(layout, structure):
    # a country page is a structure with 3 "columns":
    # column-1 has an image and a select box to select other countries
    # column-2 has is a structure of tabs and tables
    # column-3 is unknown and will be ignored

    payload = structure['column-2'][0]
    portletid, records = payload
    country = {'Summary': []}
    for record in records['content']:
        type_, id, payload = record
        if type_ == 'text':
            country[id] = payload[0]
        if type_ == 'dynamic':
            for info in record[2]:
                if isinstance(info, basestring):
                    continue
                t, name, text = info
                country['Summary'].append((name, text[0]))

    column1_content = structure['column-1'][0]
    portletid, records = column1_content
    image_info = {
        'id': records['content'][0][2][0],
        'description': records['description'],
        'title': records['title'],
    }
    country['image'] = image_info
    country['name'] = structure['name']

    # TODO:
    # create_country(country)


def import_template_ace_layout_2(layout, structure):
    pass


def import_template_ace_layout_col_1_2(layout, structure):
    print layout.friendlyurl
    # import pdb; pdb.set_trace()


def import_template_ast(layout, structure):
    # TODO: create ast page based on structure
    # column-1 has the imagemap on the left side
    # column-2 has 2 portlets:  title and then the one with content (which also
    # has a title)

    image_portlet = structure['column-1'][0][1]['content'][0]
    header_text = structure['column-2'][0][1]['headertext']
    content = structure['column-2'][1][1]['content'][0]

    noop(image_portlet, header_text, content)


def import_template_urban_ast(layout, structure):
    # TODO: create urbanast page based on structure
    # column-1 has the imagemap on the left side
    # column-2 has 2 portlets:  title and then the one with content (which also
    # has a title)
    image_portlet = structure['column-1'][0][1]['content'][0]
    header_text = structure['column-2'][0][1]['headertext']
    content = structure['column-2'][1][1]['content'][0]

    noop(image_portlet, header_text, content)


def run_importer():
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

    site = get_plone_site()

    structure = ['content', 'aceprojects', 'casestudy',
                 'adaptationoption', 'repository']
    for name in (set(structure) - set(site.objectIds())):
        site.invokeFactory("Folder", name)

    for layout in session.query(sql.Layout).filter_by(privatelayout=False):
        import_layout(layout, site)

    import pprint
    pprint.pprint(dict(MAPOFLAYOUTS))
    # import pdb; pdb.set_trace()
    raise ValueError

    content_destination = site['content']
    for aceitem in session.query(sql.AceAceitem):
        import_aceitem(aceitem, content_destination)

    aceprojects_destination = site['aceprojects']
    for aceproject in session.query(sql.AceProject):
        import_aceproject(aceproject, aceprojects_destination)

    casestudy_destination = site['casestudy']
    adaptationoption_destination = site['adaptationoption']
    for acemeasure in session.query(sql.AceMeasure):
        if acemeasure.mao_type == 'A':
            import_casestudy(acemeasure, casestudy_destination)
        else:
            import_adaptationoption(acemeasure, adaptationoption_destination)

    documents_destination = site['repository']
    for image in session.query(sql.Image):
        import_image(image, documents_destination)
    for dlfileentry in session.query(sql.Dlfileentry):
        import_dlfileentry(dlfileentry, documents_destination)


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


# sql.AceAceitem.company = relationship(sql.Company,
#                                       foreign_keys=sql.AceAceitem.companyid,
#                                       backref="aceitems",
#                                       primaryjoin="and_(Company.companyid==AceAceitem.companyid)")
