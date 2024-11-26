from sqlalchemy import Column, BigInteger, String, Text, DateTime   #, text
from eea.climateadapt._importer import sqlschema as sql
from sqlalchemy.orm import relationship
import logging


logger = logging.getLogger('eea.climateadapt.importer')
# logger.setLevel(logging.INFO)
# logger.addHandler(logging.StreamHandler())


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



def fix_relations(session):
    try:
        for kname, rels in list(RELATIONS.items()):
            logger.info("Setting relations for %s", kname)
            klass = getattr(sql, kname)
            for name, info in list(rels.items()):
                other = getattr(sql, info['other'])
                pj = "and_(%s.%s==%s.%s)" % (info['other'], info['fk'], kname,
                                            info['fk'])
                rel = relationship(other,
                                foreign_keys=getattr(klass, info['fk']),
                                backref=info['bref'],
                                primaryjoin=pj,
                                )
                setattr(klass, name, rel)
        sql.AceAceitem.metadata_ = Column('metadata', Text)
    except Exception as e:
        logger.warning("Error in setting database relationship: %s", e)


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
