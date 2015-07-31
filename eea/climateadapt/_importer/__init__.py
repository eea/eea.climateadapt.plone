from eea.climateadapt._importer import sqlschema as sql
from plone.dexterity.utils import createContentInContainer
from sqlalchemy import Column, BigInteger, String, Text, DateTime   #, text
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from zope.sqlalchemy import register
import logging
import os
import transaction

logger = logging.getLogger('eea.climateadapt.importer')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


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


def s2l(text, separator=';'):
    """Converts a string in form: u'EXTREMETEMP;FLOODING;' to a list"""
    return filter(None, text.split(separator))


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


def import_aceitem(data, session, location):
    # TODO: Some AceItems have ACTION, MEASURE, REASEARCHPROJECT types and
    # should be mapped over AceMeasure and AceProject

    if data.datatype in ACE_ITEM_TYPES:
        item = createContentInContainer(
            location,
            ACE_ITEM_TYPES[data.datatype],
            title=data.name,
            data_type=s2l(data.datatype),
            storage_type=s2l(data.storagetype),
            sectors=s2l(data.sectors_),
        )

        return item


def import_aceproject(data, session, location):
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

    return item


def import_adaptationoption(data, session, location):
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

    return item


def import_casestudy(data, session, location):
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

    return item


def run_importer(session):
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

    site = get_plone_site()

    if not ('content' in site.objectIds()):
        site.invokeFactory("Folder", 'content')

    content_destination = site['content']

    for aceitem in session.query(sql.AceAceitem):
        import_aceitem(aceitem, session, content_destination)

    print content_destination.objectIds()

    if not ('aceprojects' in site.objectIds()):
        site.invokeFactory("Folder", 'aceprojects')

    aceprojects_destination = site['aceprojects']
    for aceproject in session.query(sql.AceProject):
        import_aceproject(aceproject, session, aceprojects_destination)

    if not ('casestudy' in site.objectIds()):
        site.invokeFactory("Folder", 'casestudy')
    if not ('adaptationoption' in site.objectIds()):
        site.invokeFactory("Folder", 'adaptationoption')

    casestudy_destination = site['casestudy']
    adaptationoption_destination = site['adaptationoption']
    for acemeasure in session.query(sql.AceMeasure):
        if acemeasure.mao_type == 'A':
            import_casestudy(acemeasure, session, casestudy_destination)
        else:
            import_adaptationoption(acemeasure, session,
                                    adaptationoption_destination)


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
    engine = create_engine(os.environ.get("DB"))
    Session = scoped_session(sessionmaker(bind=engine))
    register(Session, keep_session=True)
    session = Session()
    run_importer(session)
    transaction.commit()

    return


# sql.AceAceitem.company = relationship(sql.Company,
#                                       foreign_keys=sql.AceAceitem.companyid,
#                                       backref="aceitems",
#                                       primaryjoin="and_(Company.companyid==AceAceitem.companyid)")
