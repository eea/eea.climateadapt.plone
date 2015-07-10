# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Float, Index, Integer, LargeBinary, Numeric, SmallInteger, String, Table, Text, text
from sqlalchemy.dialects.postgresql.base import OID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

Base = declarative_base()
metadata = MetaData()

class Account(Base):
    __tablename__ = 'account_'

    accountid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    parentaccountid = Column(BigInteger)
    name = Column(String(75))
    legalname = Column(String(75))
    legalid = Column(String(75))
    legaltype = Column(String(75))
    siccode = Column(String(75))
    tickersymbol = Column(String(75))
    industry = Column(String(75))
    type_ = Column(String(75))
    size_ = Column(String(75))


class AceAceitem(Base):
    __tablename__ = 'ace_aceitem'

    aceitemid = Column(BigInteger, primary_key=True, server_default=text("nextval('ace_aceitem_id_seq'::regclass)"))
    companyid = Column(BigInteger)
    groupid = Column(BigInteger, index=True)
    wxsharvesterid = Column(BigInteger)
    name = Column(String(255))
    description = Column(Text)
    datatype = Column(String(255))
    storedat = Column(Text)
    storagetype = Column(String(255))
    specialtagging = Column(String(75), server_default=text("NULL::character varying"))
    textsearch = Column(Text)
    keyword = Column(Text)
    targetresolution = Column(String(255))
    spatiallayer = Column(String(150))
    spatialvalues = Column(String(255))
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    publicationdate = Column(DateTime)
    sectors_ = Column(String(255))
    elements_ = Column(String(255))
    climateimpacts_ = Column(String(255))
    rating = Column(BigInteger)
    importance = Column(BigInteger)
    source = Column(Text)
    deeplink = Column(Text)
    controlstatus = Column(SmallInteger)
    creator = Column(String(75))
    creationdate = Column(DateTime)
    moderator = Column(String(2000))
    approvaldate = Column(DateTime)
    replacesid = Column(BigInteger)
    comments = Column(Text)
    textwebpage = Column(Text)
    cswharvesterid = Column(BigInteger)
    year = Column(String(7))
    geochars = Column(Text)
    feature = Column(String(75))
    supdocs = Column(String(50))
    admincomment = Column(Text)
    lockdate = Column(DateTime)
    scenario = Column(String(3000))
    timeperiod = Column(String(75))


class AceCswharvester(Base):
    __tablename__ = 'ace_cswharvester'

    cswharvesterid = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    url = Column(String(255))
    freetext = Column(String(75))
    title = Column(String(75))
    abstrakt = Column(String(75))
    subject = Column(String(75))
    every = Column(Integer)
    topic = Column(String(75))
    status = Column(String(75))
    savedtogeonetwork = Column(Boolean)
    geonetworkid = Column(BigInteger)
    geonetworkuuid = Column(String(75))
    companyid = Column(BigInteger)
    groupid = Column(BigInteger)
    type_ = Column(String(75))
    username = Column(String(75))
    password_ = Column(String(75))


t_ace_indicator = Table(
    'ace_indicator', metadata,
    Column('aceitemid', BigInteger),
    Column('companyid', BigInteger),
    Column('groupid', BigInteger),
    Column('nasid', BigInteger),
    Column('name', String(255)),
    Column('description', Text),
    Column('datatype', String(255)),
    Column('storedat', String(255)),
    Column('storagetype', String(255)),
    Column('language', String(24)),
    Column('textsearch', Text),
    Column('keyword', String(2048)),
    Column('targetresolution', String(255)),
    Column('spatiallayer', String(150)),
    Column('spatialvalues', String(255)),
    Column('startdate', DateTime),
    Column('enddate', DateTime),
    Column('publicationdate', DateTime),
    Column('sectors_', String(255)),
    Column('elements_', String(255)),
    Column('climateimpacts_', String(255)),
    Column('rating', BigInteger),
    Column('importance', BigInteger)
)


class AceMeasure(Base):
    __tablename__ = 'ace_measure'

    measureid = Column(BigInteger, primary_key=True, server_default=text("nextval('ace_measure_id_seq'::regclass)"))
    companyid = Column(BigInteger)
    groupid = Column(BigInteger)
    name = Column(String(255))
    description = Column(Text)
    implementationtype = Column(Text)
    implementationtime = Column(String(255))
    lifetime = Column(Text)
    spatiallayer = Column(Text)
    spatialvalues = Column(Text)
    legalaspects = Column(Text)
    stakeholderparticipation = Column(Text)
    contact = Column(Text)
    succeslimitations = Column(Text)
    website = Column(Text)
    costbenefit = Column(Text)
    keywords = Column(Text)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    publicationdate = Column(DateTime)
    specialtagging = Column(String(75), server_default=text("NULL::character varying"))
    sectors_ = Column(String(255))
    elements_ = Column(String(255))
    climateimpacts_ = Column(String(255))
    mao_type = Column(String(24))
    source = Column(Text)
    rating = Column(BigInteger)
    importance = Column(BigInteger)
    lon = Column(Float(53))
    lat = Column(Float(53))
    satarea = Column(String(254))
    controlstatus = Column(SmallInteger)
    creator = Column(String(75))
    creationdate = Column(DateTime)
    moderator = Column(String(2000))
    approvaldate = Column(DateTime)
    replacesid = Column(BigInteger)
    comments = Column(Text)
    textwebpage = Column(Text)
    admincomment = Column(Text)
    casestudyfeature = Column(String(50))
    objectives = Column(Text)
    challenges = Column(Text)
    adaptationoptions = Column(String(2500))
    solutions = Column(Text)
    relevance = Column(String(2500))
    primephoto = Column(String(10))
    supphotos = Column(String(50))
    supdocs = Column(String(50))
    year = Column(String(7))
    geos_ = Column(String(250))
    geochars = Column(Text)
    category = Column(String(50))
    lockdate = Column(DateTime)


class AceProject(Base):
    __tablename__ = 'ace_project'

    projectid = Column(BigInteger, primary_key=True, server_default=text("nextval('ace_project_id_seq'::regclass)"))
    companyid = Column(BigInteger)
    groupid = Column(BigInteger, index=True)
    acronym = Column(String(75))
    title = Column(String(255))
    startdate = Column(Date)
    enddate = Column(Date)
    lead = Column(String(255))
    partners = Column(Text)
    funding = Column(String(100))
    sectors = Column(String(255))
    spatiallayer = Column(String(150))
    abstracts = Column(Text)
    element = Column(String(255))
    keywords = Column(Text)
    website = Column(Text)
    duration = Column(String(255))
    rating = Column(BigInteger)
    importance = Column(BigInteger)
    specialtagging = Column(String(75))
    controlstatus = Column(SmallInteger)
    creator = Column(String(75))
    creationdate = Column(DateTime)
    moderator = Column(String(2000))
    approvaldate = Column(DateTime)
    replacesid = Column(BigInteger)
    comments = Column(Text)
    textwebpage = Column(Text)
    spatialvalues = Column(String(255))
    source = Column(String(1024))
    climateimpacts = Column(String(255))
    supdocs = Column(String(50))
    feature = Column(String(75))
    geochars = Column(Text)
    lockdate = Column(DateTime)
    admincomment = Column(Text)


class AceWxsharvester(Base):
    __tablename__ = 'ace_wxsharvester'

    wxsharvesterid = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    url = Column(String(255))
    ogctype = Column(String(75))
    every = Column(Integer)
    topic = Column(String(75))
    savedtogeonetwork = Column(Boolean)
    geonetworkid = Column(BigInteger)
    geonetworkuuid = Column(String(75))
    companyid = Column(BigInteger)
    groupid = Column(BigInteger)
    status = Column(String(75))


class Addres(Base):
    __tablename__ = 'address'
    __table_args__ = (
        Index('ix_923bd178', 'companyid', 'classnameid', 'classpk', 'mailing'),
        Index('ix_8fcb620e', 'uuid_', 'companyid'),
        Index('ix_9226dbb4', 'companyid', 'classnameid', 'classpk', 'primary_'),
        Index('ix_71cb1123', 'companyid', 'classnameid', 'classpk'),
        Index('ix_abd7dac0', 'companyid', 'classnameid')
    )

    addressid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    street1 = Column(String(75))
    street2 = Column(String(75))
    street3 = Column(String(75))
    city = Column(String(75))
    zip = Column(String(75))
    regionid = Column(BigInteger)
    countryid = Column(BigInteger)
    typeid = Column(Integer)
    mailing = Column(Boolean)
    primary_ = Column(Boolean)
    uuid_ = Column(String(75), index=True)


class Announcementsdelivery(Base):
    __tablename__ = 'announcementsdelivery'
    __table_args__ = (
        Index('ix_ba4413d5', 'userid', 'type_', unique=True),
    )

    deliveryid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    type_ = Column(String(75))
    email = Column(Boolean)
    sms = Column(Boolean)
    website = Column(Boolean)


class Announcementsentry(Base):
    __tablename__ = 'announcementsentry'
    __table_args__ = (
        Index('ix_a6ef0b81', 'classnameid', 'classpk'),
        Index('ix_14f06a6b', 'classnameid', 'classpk', 'alert'),
        Index('ix_f2949120', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    entryid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    title = Column(String(75))
    content = Column(Text)
    url = Column(Text)
    type_ = Column(String(75))
    displaydate = Column(DateTime)
    expirationdate = Column(DateTime)
    priority = Column(Integer)
    alert = Column(Boolean)


class Announcementsflag(Base):
    __tablename__ = 'announcementsflag'
    __table_args__ = (
        Index('ix_4539a99c', 'userid', 'entryid', 'value', unique=True),
    )

    flagid = Column(BigInteger, primary_key=True)
    userid = Column(BigInteger)
    createdate = Column(DateTime)
    entryid = Column(BigInteger, index=True)
    value = Column(Integer)


class Assetcategory(Base):
    __tablename__ = 'assetcategory'
    __table_args__ = (
        Index('ix_b185e980', 'parentcategoryid', 'vocabularyid'),
        Index('ix_87603842', 'groupid', 'parentcategoryid', 'vocabularyid'),
        Index('ix_be4df2bf', 'parentcategoryid', 'name', 'vocabularyid', unique=True),
        Index('ix_c7f39fca', 'groupid', 'name', 'vocabularyid'),
        Index('ix_510b46ac', 'groupid', 'parentcategoryid', 'name'),
        Index('ix_e8d019aa', 'uuid_', 'groupid', unique=True),
        Index('ix_bbaf6928', 'uuid_', 'companyid'),
        Index('ix_2008facb', 'groupid', 'vocabularyid'),
        Index('ix_d61abe08', 'name', 'vocabularyid'),
        Index('ix_852ea801', 'groupid', 'parentcategoryid', 'name', 'vocabularyid'),
        Index('ix_9ddd15ea', 'parentcategoryid', 'name')
    )

    uuid_ = Column(String(75), index=True)
    categoryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    parentcategoryid = Column(BigInteger, index=True)
    leftcategoryid = Column(BigInteger)
    rightcategoryid = Column(BigInteger)
    name = Column(String(75))
    title = Column(Text)
    vocabularyid = Column(BigInteger, index=True)
    description = Column(Text)


class Assetcategoryproperty(Base):
    __tablename__ = 'assetcategoryproperty'
    __table_args__ = (
        Index('ix_52340033', 'companyid', 'key_'),
        Index('ix_dbd111aa', 'categoryid', 'key_', unique=True)
    )

    categorypropertyid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    categoryid = Column(BigInteger, index=True)
    key_ = Column(String(75))
    value = Column(String(75))


class AssetentriesAssetcategory(Base):
    __tablename__ = 'assetentries_assetcategories'

    entryid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    categoryid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class AssetentriesAssettag(Base):
    __tablename__ = 'assetentries_assettags'

    entryid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    tagid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class Assetentry(Base):
    __tablename__ = 'assetentry'
    __table_args__ = (
        Index('ix_1eba6821', 'groupid', 'classuuid'),
        Index('ix_1e9d371d', 'classnameid', 'classpk', unique=True)
    )

    entryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    classuuid = Column(String(75), index=True)
    visible = Column(Boolean, index=True)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    publishdate = Column(DateTime, index=True)
    expirationdate = Column(DateTime, index=True)
    mimetype = Column(String(75))
    title = Column(Text)
    description = Column(Text)
    summary = Column(Text)
    url = Column(Text)
    height = Column(Integer)
    width = Column(Integer)
    priority = Column(Float(53))
    viewcount = Column(Integer)
    classtypeid = Column(BigInteger)
    layoutuuid = Column(String(75), index=True)


class Assetlink(Base):
    __tablename__ = 'assetlink'
    __table_args__ = (
        Index('ix_8f542794', 'entryid1', 'entryid2', 'type_'),
        Index('ix_91f132c', 'entryid2', 'type_'),
        Index('ix_14d5a20d', 'entryid1', 'type_'),
        Index('ix_56e0ab21', 'entryid1', 'entryid2')
    )

    linkid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    entryid1 = Column(BigInteger, index=True)
    entryid2 = Column(BigInteger, index=True)
    type_ = Column(Integer)
    weight = Column(Integer)


class Assettag(Base):
    __tablename__ = 'assettag'
    __table_args__ = (
        Index('ix_d63322f9', 'groupid', 'name'),
    )

    tagid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    assetcount = Column(Integer)


class Assettagproperty(Base):
    __tablename__ = 'assettagproperty'
    __table_args__ = (
        Index('ix_13805bf7', 'companyid', 'key_'),
        Index('ix_2c944354', 'tagid', 'key_', unique=True)
    )

    tagpropertyid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    tagid = Column(BigInteger, index=True)
    key_ = Column(String(75))
    value = Column(String(255))


class Assettagstat(Base):
    __tablename__ = 'assettagstats'
    __table_args__ = (
        Index('ix_56682cc4', 'tagid', 'classnameid', unique=True),
    )

    tagstatsid = Column(BigInteger, primary_key=True)
    tagid = Column(BigInteger, index=True)
    classnameid = Column(BigInteger, index=True)
    assetcount = Column(Integer)


class Assetvocabulary(Base):
    __tablename__ = 'assetvocabulary'
    __table_args__ = (
        Index('ix_c0aad74d', 'groupid', 'name', unique=True),
        Index('ix_c4e6fd10', 'uuid_', 'companyid'),
        Index('ix_1b2b8792', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    vocabularyid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    title = Column(Text)
    description = Column(Text)
    settings_ = Column(Text)


class Backgroundtask(Base):
    __tablename__ = 'backgroundtask'
    __table_args__ = (
        Index('ix_7e757d70', 'groupid', 'taskexecutorclassname', 'status'),
        Index('ix_7a9ff471', 'groupid', 'taskexecutorclassname', 'completed'),
        Index('ix_2fcfe748', 'taskexecutorclassname', 'status'),
        Index('ix_98cc0aab', 'groupid', 'name', 'taskexecutorclassname'),
        Index('ix_a73b688a', 'groupid', 'taskexecutorclassname'),
        Index('ix_579c63b0', 'groupid', 'name', 'taskexecutorclassname', 'completed'),
        Index('ix_c71c3b7', 'groupid', 'status')
    )

    backgroundtaskid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75), index=True)
    servletcontextnames = Column(String(255))
    taskexecutorclassname = Column(String(200))
    taskcontext = Column(Text)
    completed = Column(Boolean)
    completiondate = Column(DateTime)
    status = Column(Integer, index=True)
    statusmessage = Column(Text)


class Blogsentry(Base):
    __tablename__ = 'blogsentry'
    __table_args__ = (
        Index('ix_430d791f', 'companyid', 'displaydate'),
        Index('ix_621e19d', 'groupid', 'displaydate'),
        Index('ix_da04f689', 'groupid', 'userid', 'displaydate', 'status'),
        Index('ix_f0e73383', 'groupid', 'displaydate', 'status'),
        Index('ix_5e8307bb', 'uuid_', 'companyid'),
        Index('ix_bb0c2905', 'companyid', 'displaydate', 'status'),
        Index('ix_1efd8ee9', 'groupid', 'status'),
        Index('ix_49e15a23', 'groupid', 'userid', 'status'),
        Index('ix_eb2dce27', 'companyid', 'status'),
        Index('ix_db780a20', 'groupid', 'urltitle', unique=True),
        Index('ix_a5f57b61', 'companyid', 'userid', 'status'),
        Index('ix_8cace77b', 'companyid', 'userid'),
        Index('ix_2672f77f', 'displaydate', 'status'),
        Index('ix_fbde0aa3', 'groupid', 'userid', 'displaydate'),
        Index('ix_1b1040fd', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    entryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    title = Column(String(150))
    urltitle = Column(String(150))
    content = Column(Text)
    displaydate = Column(DateTime)
    allowpingbacks = Column(Boolean)
    allowtrackbacks = Column(Boolean)
    trackbacks = Column(Text)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)
    description = Column(Text)
    smallimage = Column(Boolean)
    smallimageid = Column(String(75))
    smallimageurl = Column(Text)


class Blogsstatsuser(Base):
    __tablename__ = 'blogsstatsuser'
    __table_args__ = (
        Index('ix_507ba031', 'userid', 'lastpostdate'),
        Index('ix_28c78d5c', 'groupid', 'entrycount'),
        Index('ix_82254c25', 'groupid', 'userid', unique=True),
        Index('ix_90cda39a', 'companyid', 'entrycount')
    )

    statsuserid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    entrycount = Column(Integer)
    lastpostdate = Column(DateTime)
    ratingstotalentries = Column(Integer)
    ratingstotalscore = Column(Float(53))
    ratingsaveragescore = Column(Float(53))


class Bookmarksentry(Base):
    __tablename__ = 'bookmarksentry'
    __table_args__ = (
        Index('ix_eaa02a91', 'uuid_', 'groupid', unique=True),
        Index('ix_89bedc4f', 'uuid_', 'companyid'),
        Index('ix_416ad7d5', 'groupid', 'status'),
        Index('ix_5200100c', 'groupid', 'folderid'),
        Index('ix_e2e9f129', 'groupid', 'userid'),
        Index('ix_9d9cf70f', 'groupid', 'userid', 'status'),
        Index('ix_146382f2', 'groupid', 'folderid', 'status'),
        Index('ix_276c8c13', 'companyid', 'status'),
        Index('ix_c78b61ac', 'groupid', 'userid', 'folderid', 'status')
    )

    uuid_ = Column(String(75), index=True)
    entryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    folderid = Column(BigInteger)
    name = Column(String(255))
    url = Column(Text)
    visits = Column(Integer)
    priority = Column(Integer)
    username = Column(String(75))
    resourceblockid = Column(BigInteger, index=True)
    description = Column(Text)
    treepath = Column(Text)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Bookmarksfolder(Base):
    __tablename__ = 'bookmarksfolder'
    __table_args__ = (
        Index('ix_967799c0', 'groupid', 'parentfolderid'),
        Index('ix_54f0ed65', 'uuid_', 'companyid'),
        Index('ix_d16018a6', 'groupid', 'parentfolderid', 'status'),
        Index('ix_c27c9dbd', 'companyid', 'status'),
        Index('ix_dc2f8927', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    folderid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    parentfolderid = Column(BigInteger)
    name = Column(String(75))
    description = Column(Text)
    username = Column(String(75))
    resourceblockid = Column(BigInteger, index=True)
    treepath = Column(Text)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Browsertracker(Base):
    __tablename__ = 'browsertracker'

    browsertrackerid = Column(BigInteger, primary_key=True)
    userid = Column(BigInteger, unique=True)
    browserkey = Column(BigInteger)


class Calendar(Base):
    __tablename__ = 'calendar'
    __table_args__ = (
        Index('ix_b53eb0e1', 'groupid', 'calendarresourceid'),
        Index('ix_97fc174e', 'groupid', 'calendarresourceid', 'defaultcalendar'),
        Index('ix_3ae311a', 'uuid_', 'groupid', unique=True),
        Index('ix_97656498', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    calendarid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    resourceblockid = Column(BigInteger, index=True)
    calendarresourceid = Column(BigInteger)
    name = Column(Text)
    description = Column(Text)
    color = Column(Integer)
    defaultcalendar = Column(Boolean)
    enablecomments = Column(Boolean)
    enableratings = Column(Boolean)


class Calendarbooking(Base):
    __tablename__ = 'calendarbooking'
    __table_args__ = (
        Index('ix_113a264e', 'calendarid', 'parentcalendarbookingid', unique=True),
        Index('ix_f7b8a941', 'parentcalendarbookingid', 'status'),
        Index('ix_470170b4', 'calendarid', 'status'),
        Index('ix_f4c61797', 'uuid_', 'groupid', unique=True),
        Index('ix_a21d9fd5', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    calendarbookingid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    resourceblockid = Column(BigInteger, index=True)
    calendarid = Column(BigInteger, index=True)
    calendarresourceid = Column(BigInteger, index=True)
    parentcalendarbookingid = Column(BigInteger, index=True)
    title = Column(Text)
    description = Column(Text)
    location = Column(Text)
    starttime = Column(BigInteger)
    endtime = Column(BigInteger)
    allday = Column(Boolean)
    recurrence = Column(Text)
    firstreminder = Column(BigInteger)
    firstremindertype = Column(String(75))
    secondreminder = Column(BigInteger)
    secondremindertype = Column(String(75))
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Calendarnotificationtemplate(Base):
    __tablename__ = 'calendarnotificationtemplate'
    __table_args__ = (
        Index('ix_4d7d97bd', 'uuid_', 'companyid'),
        Index('ix_7727a482', 'calendarid', 'notificationtype', 'notificationtemplatetype'),
        Index('ix_4012e97f', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    calendarnotificationtemplateid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    calendarid = Column(BigInteger, index=True)
    notificationtype = Column(String(75))
    notificationtypesettings = Column(String(75))
    notificationtemplatetype = Column(String(75))
    subject = Column(String(75))
    body = Column(Text)


class Calendarresource(Base):
    __tablename__ = 'calendarresource'
    __table_args__ = (
        Index('ix_4470a59d', 'companyid', 'code_', 'active_'),
        Index('ix_40678371', 'groupid', 'active_'),
        Index('ix_56a06bc6', 'uuid_', 'companyid'),
        Index('ix_16a12327', 'classnameid', 'classpk', unique=True),
        Index('ix_55c2f8aa', 'groupid', 'code_'),
        Index('ix_4abd2bc8', 'uuid_', 'groupid', unique=True),
        Index('ix_2c5184d4', 'companyid', 'name', 'active_'),
        Index('ix_b9ea8c92', 'groupid', 'name', 'active_')
    )

    uuid_ = Column(String(75), index=True)
    calendarresourceid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    resourceblockid = Column(BigInteger, index=True)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    classuuid = Column(String(75))
    code_ = Column(String(75))
    name = Column(Text)
    description = Column(Text)
    active_ = Column(Boolean, index=True)


class Calevent(Base):
    __tablename__ = 'calevent'
    __table_args__ = (
        Index('ix_299639c6', 'uuid_', 'companyid'),
        Index('ix_fcd7c63d', 'groupid', 'type_'),
        Index('ix_4fddd2bf', 'groupid', 'repeating'),
        Index('ix_5cce79c8', 'uuid_', 'groupid', unique=True),
        Index('ix_fd93cbfa', 'groupid', 'type_', 'repeating')
    )

    uuid_ = Column(String(75), index=True)
    eventid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    title = Column(String(75))
    description = Column(Text)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    durationhour = Column(Integer)
    durationminute = Column(Integer)
    allday = Column(Boolean)
    timezonesensitive = Column(Boolean)
    type_ = Column(String(75))
    repeating = Column(Boolean)
    recurrence = Column(Text)
    remindby = Column(Integer, index=True)
    firstreminder = Column(Integer)
    secondreminder = Column(Integer)
    location = Column(Text)


class ChatEntry(Base):
    __tablename__ = 'chat_entry'
    __table_args__ = (
        Index('ix_d9e49928', 'createdate', 'fromuserid', 'touserid'),
        Index('ix_2a17a23f', 'fromuserid', 'touserid', 'content'),
        Index('ix_ad559d93', 'createdate', 'fromuserid'),
        Index('ix_8be273a4', 'createdate', 'touserid')
    )

    entryid = Column(BigInteger, primary_key=True)
    createdate = Column(BigInteger, index=True)
    fromuserid = Column(BigInteger, index=True)
    touserid = Column(BigInteger, index=True)
    content = Column(String(1000))


class ChatStatu(Base):
    __tablename__ = 'chat_status'
    __table_args__ = (
        Index('ix_b723b792', 'modifieddate', 'online_'),
    )

    statusid = Column(BigInteger, primary_key=True)
    userid = Column(BigInteger, unique=True)
    modifieddate = Column(BigInteger, index=True)
    online_ = Column(Boolean, index=True)
    awake = Column(Boolean)
    activepanelid = Column(String(75))
    message = Column(Text)
    playsound = Column(Boolean)


class Classname(Base):
    __tablename__ = 'classname_'

    classnameid = Column(BigInteger, primary_key=True)
    value = Column(String(200), unique=True)


class ClimwatExc(Base):
    __tablename__ = 'climwat_exc'

    m_category = Column(String(255))
    name = Column(String(255))
    description = Column(Text)
    scarcity_drought = Column(String(255))
    flooding_sea = Column(String(255))
    water_quality_biod = Column(String(255))
    snow_ = Column('snow ', String(255))
    reference = Column(Text)
    water_management = Column(String(255))
    agriculture = Column(String(255))
    energy = Column(String(255))
    industry = Column(String(255))
    forestry = Column(String(255))
    shipping = Column(String(255))
    domestic_tourism = Column(String(255))
    short_term_5_25 = Column(String(255))
    mid_long_term = Column(String(255))
    cost_investment = Column(String(255))
    cost_operational = Column(String(255))
    national = Column(String(255))
    regional = Column(String(255))
    municipality_company = Column(String(255))
    institutional_req = Column(String(255))
    combi_measures = Column(String(255))
    urg_prio = Column(String(255))
    feasibility = Column(String(255))
    _publ_participation = Column(' publ_participation', String(255))
    flexibility = Column(String(255))
    robustness = Column(String(255))
    id = Column(Float(53), primary_key=True)
    sectors_ = Column(String(255))
    climateimpacts_ = Column(String(255))
    spatiallayer = Column(String(75))
    implementationtime = Column(String(255))


class Clustergroup(Base):
    __tablename__ = 'clustergroup'

    clustergroupid = Column(BigInteger, primary_key=True)
    name = Column(String(75))
    clusternodeids = Column(String(75))
    wholecluster = Column(Boolean)


class Company(Base):
    __tablename__ = 'company'

    companyid = Column(BigInteger, primary_key=True)
    accountid = Column(BigInteger)
    webid = Column(String(75), unique=True)
    key_ = Column(Text)
    mx = Column(String(75), index=True)
    homeurl = Column(Text)
    logoid = Column(BigInteger, index=True)
    system = Column(Boolean, index=True)
    maxusers = Column(Integer)
    active_ = Column(Boolean)


class Contact(Base):
    __tablename__ = 'contact_'
    __table_args__ = (
        Index('ix_791914fa', 'classnameid', 'classpk'),
    )

    contactid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    accountid = Column(BigInteger, index=True)
    parentcontactid = Column(BigInteger)
    firstname = Column(String(75))
    middlename = Column(String(75))
    lastname = Column(String(75))
    prefixid = Column(Integer)
    suffixid = Column(Integer)
    male = Column(Boolean)
    birthday = Column(DateTime)
    smssn = Column(String(75))
    aimsn = Column(String(75))
    facebooksn = Column(String(75))
    icqsn = Column(String(75))
    jabbersn = Column(String(75))
    msnsn = Column(String(75))
    myspacesn = Column(String(75))
    skypesn = Column(String(75))
    twittersn = Column(String(75))
    ymsn = Column(String(75))
    employeestatusid = Column(String(75))
    employeenumber = Column(String(75))
    jobtitle = Column(String(100))
    jobclass = Column(String(75))
    hoursofoperation = Column(String(75))
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    emailaddress = Column(String(75))


class Counter(Base):
    __tablename__ = 'counter'

    name = Column(String(75), primary_key=True)
    currentid = Column(BigInteger)


class Country(Base):
    __tablename__ = 'country'

    countryid = Column(BigInteger, primary_key=True)
    name = Column(String(75), unique=True)
    a2 = Column(String(75), unique=True)
    a3 = Column(String(75), unique=True)
    number_ = Column(String(75))
    idd_ = Column(String(75))
    active_ = Column(Boolean, index=True)
    ziprequired = Column(Boolean)


class Cyrususer(Base):
    __tablename__ = 'cyrususer'

    userid = Column(String(75), primary_key=True)
    password_ = Column(String(75), nullable=False)


class Cyrusvirtual(Base):
    __tablename__ = 'cyrusvirtual'

    emailaddress = Column(String(75), primary_key=True)
    userid = Column(String(75), nullable=False)


class Ddlrecord(Base):
    __tablename__ = 'ddlrecord'
    __table_args__ = (
        Index('ix_384ab6f7', 'uuid_', 'companyid'),
        Index('ix_aac564d3', 'recordsetid', 'userid'),
        Index('ix_b4328f39', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    recordid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    versionuserid = Column(BigInteger)
    versionusername = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    ddmstorageid = Column(BigInteger)
    recordsetid = Column(BigInteger, index=True)
    version = Column(String(75))
    displayindex = Column(Integer)


class Ddlrecordset(Base):
    __tablename__ = 'ddlrecordset'
    __table_args__ = (
        Index('ix_5938c39f', 'uuid_', 'companyid'),
        Index('ix_56dab121', 'groupid', 'recordsetkey', unique=True),
        Index('ix_270ba5e1', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    recordsetid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    ddmstructureid = Column(BigInteger)
    recordsetkey = Column(String(75))
    name = Column(Text)
    description = Column(Text)
    mindisplayrows = Column(Integer)
    scope = Column(Integer)


class Ddlrecordversion(Base):
    __tablename__ = 'ddlrecordversion'
    __table_args__ = (
        Index('ix_c79e347', 'recordid', 'version', unique=True),
        Index('ix_762adc7', 'recordid', 'status')
    )

    recordversionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    ddmstorageid = Column(BigInteger)
    recordsetid = Column(BigInteger)
    recordid = Column(BigInteger, index=True)
    version = Column(String(75))
    displayindex = Column(Integer)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Ddmcontent(Base):
    __tablename__ = 'ddmcontent'
    __table_args__ = (
        Index('ix_eb9bde28', 'uuid_', 'groupid', unique=True),
        Index('ix_3a9c0626', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    contentid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(Text)
    description = Column(Text)
    xml = Column(Text)


class Ddmstoragelink(Base):
    __tablename__ = 'ddmstoragelink'

    uuid_ = Column(String(75), index=True)
    storagelinkid = Column(BigInteger, primary_key=True)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger, unique=True)
    structureid = Column(BigInteger, index=True)


class Ddmstructure(Base):
    __tablename__ = 'ddmstructure'
    __table_args__ = (
        Index('ix_85c7ebe2', 'uuid_', 'groupid', unique=True),
        Index('ix_f9fb8d60', 'uuid_', 'companyid'),
        Index('ix_43395316', 'groupid', 'parentstructureid'),
        Index('ix_c8785130', 'groupid', 'classnameid', 'structurekey', unique=True),
        Index('ix_b6ed5e50', 'groupid', 'classnameid'),
        Index('ix_4fbac092', 'companyid', 'classnameid')
    )

    uuid_ = Column(String(75), index=True)
    structureid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger, index=True)
    structurekey = Column(String(75), index=True)
    name = Column(Text)
    description = Column(Text)
    xsd = Column(Text)
    storagetype = Column(String(75))
    type_ = Column(Integer)
    parentstructureid = Column(BigInteger, index=True)


class Ddmstructurelink(Base):
    __tablename__ = 'ddmstructurelink'

    structurelinkid = Column(BigInteger, primary_key=True)
    classnameid = Column(BigInteger, index=True)
    classpk = Column(BigInteger, unique=True)
    structureid = Column(BigInteger, index=True)


class Ddmtemplate(Base):
    __tablename__ = 'ddmtemplate'
    __table_args__ = (
        Index('ix_b6356f93', 'classnameid', 'classpk', 'type_'),
        Index('ix_b1c33ea6', 'groupid', 'classpk'),
        Index('ix_bd9a4a91', 'groupid', 'classnameid'),
        Index('ix_824adc72', 'groupid', 'classnameid', 'classpk'),
        Index('ix_f0c3449', 'groupid', 'classnameid', 'classpk', 'type_', 'mode_'),
        Index('ix_e6dfab84', 'groupid', 'classnameid', 'templatekey', unique=True),
        Index('ix_5bc0e264', 'classpk', 'type_'),
        Index('ix_d4c2c221', 'uuid_', 'companyid'),
        Index('ix_1aa75ce3', 'uuid_', 'groupid', unique=True),
        Index('ix_5b019fe8', 'classpk', 'type_', 'mode_'),
        Index('ix_90800923', 'groupid', 'classnameid', 'classpk', 'type_')
    )

    uuid_ = Column(String(75), index=True)
    templateid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classpk = Column(BigInteger, index=True)
    name = Column(Text)
    description = Column(Text)
    type_ = Column(String(75), index=True)
    mode_ = Column(String(75))
    language = Column(String(75), index=True)
    script = Column(Text)
    cacheable = Column(Boolean)
    smallimage = Column(Boolean)
    smallimageid = Column(BigInteger, index=True)
    smallimageurl = Column(Text)
    classnameid = Column(BigInteger)
    templatekey = Column(Text, index=True)


class Dlcontent(Base):
    __tablename__ = 'dlcontent'
    __table_args__ = (
        Index('ix_eb531760', 'companyid', 'repositoryid', 'path_'),
        Index('ix_6a83a66a', 'companyid', 'repositoryid'),
        Index('ix_fdd1aaa8', 'companyid', 'repositoryid', 'path_', 'version', unique=True)
    )

    contentid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    repositoryid = Column(BigInteger)
    path_ = Column(String(255))
    version = Column(String(75))
    data_ = Column(OID)
    size_ = Column(BigInteger)


class Dlfileentry(Base):
    __tablename__ = 'dlfileentry'
    __table_args__ = (
        Index('ix_bc2e7e6a', 'uuid_', 'groupid', unique=True),
        Index('ix_29d0af28', 'groupid', 'folderid', 'fileentrytypeid'),
        Index('ix_8f6c75d0', 'folderid', 'name'),
        Index('ix_31079de8', 'uuid_', 'companyid'),
        Index('ix_93cf8193', 'groupid', 'folderid'),
        Index('ix_d20c434d', 'groupid', 'userid', 'folderid'),
        Index('ix_5391712', 'groupid', 'folderid', 'name', unique=True),
        Index('ix_43261870', 'groupid', 'userid'),
        Index('ix_ed5ca615', 'groupid', 'folderid', 'title', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    fileentryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    folderid = Column(BigInteger)
    name = Column(String(255))
    extension = Column(String(75))
    title = Column(String(255))
    description = Column(Text)
    extrasettings = Column(Text)
    version = Column(String(75))
    size_ = Column(BigInteger)
    readcount = Column(Integer)
    repositoryid = Column(BigInteger)
    mimetype = Column(String(75), index=True)
    fileentrytypeid = Column(BigInteger, index=True)
    smallimageid = Column(BigInteger)
    largeimageid = Column(BigInteger)
    custom1imageid = Column(BigInteger)
    custom2imageid = Column(BigInteger)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    treepath = Column(Text)
    manualcheckinrequired = Column(Boolean)


class Dlfileentrymetadatum(Base):
    __tablename__ = 'dlfileentrymetadata'
    __table_args__ = (
        Index('ix_a44636c9', 'fileentryid', 'fileversionid'),
        Index('ix_7332b44f', 'ddmstructureid', 'fileversionid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    fileentrymetadataid = Column(BigInteger, primary_key=True)
    ddmstorageid = Column(BigInteger)
    ddmstructureid = Column(BigInteger)
    fileentrytypeid = Column(BigInteger, index=True)
    fileentryid = Column(BigInteger, index=True)
    fileversionid = Column(BigInteger, index=True)


class Dlfileentrytype(Base):
    __tablename__ = 'dlfileentrytype'
    __table_args__ = (
        Index('ix_e9b6a85b', 'groupid', 'name', unique=True),
        Index('ix_5b6bef5f', 'groupid', 'fileentrytypekey', unique=True),
        Index('ix_1399d844', 'uuid_', 'groupid', unique=True),
        Index('ix_5b03e942', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    fileentrytypeid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(Text)
    description = Column(Text)
    fileentrytypekey = Column(Text)


class DlfileentrytypesDdmstructure(Base):
    __tablename__ = 'dlfileentrytypes_ddmstructures'

    fileentrytypeid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    structureid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class DlfileentrytypesDlfolder(Base):
    __tablename__ = 'dlfileentrytypes_dlfolders'

    fileentrytypeid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    folderid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class Dlfilerank(Base):
    __tablename__ = 'dlfilerank'
    __table_args__ = (
        Index('ix_bafb116e', 'groupid', 'userid'),
        Index('ix_4e96195b', 'groupid', 'userid', 'active_'),
        Index('ix_38f0315', 'companyid', 'userid', 'fileentryid', unique=True)
    )

    filerankid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    createdate = Column(DateTime)
    fileentryid = Column(BigInteger, index=True)
    active_ = Column(Boolean)


class Dlfileshortcut(Base):
    __tablename__ = 'dlfileshortcut'
    __table_args__ = (
        Index('ix_8571953e', 'companyid', 'status'),
        Index('ix_fdb4a946', 'uuid_', 'groupid', unique=True),
        Index('ix_17ee3098', 'groupid', 'folderid', 'active_', 'status'),
        Index('ix_348dc3b2', 'groupid', 'folderid', 'active_'),
        Index('ix_b0051937', 'groupid', 'folderid'),
        Index('ix_29ae81c4', 'uuid_', 'companyid'),
        Index('ix_ecce311d', 'groupid', 'folderid', 'status')
    )

    uuid_ = Column(String(75), index=True)
    fileshortcutid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    folderid = Column(BigInteger)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)
    repositoryid = Column(BigInteger)
    tofileentryid = Column(BigInteger, index=True)
    treepath = Column(Text)
    active_ = Column(Boolean)


class Dlfileversion(Base):
    __tablename__ = 'dlfileversion'
    __table_args__ = (
        Index('ix_d47bb14d', 'fileentryid', 'status'),
        Index('ix_a0a283f4', 'companyid', 'status'),
        Index('ix_dfd809d3', 'groupid', 'folderid', 'status'),
        Index('ix_95e9e44e', 'uuid_', 'companyid'),
        Index('ix_e2815081', 'fileentryid', 'version', unique=True),
        Index('ix_c99b2650', 'uuid_', 'groupid', unique=True),
        Index('ix_9be769ed', 'groupid', 'folderid', 'title', 'version')
    )

    fileversionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    folderid = Column(BigInteger)
    extension = Column(String(75))
    title = Column(String(255))
    description = Column(Text)
    changelog = Column(String(75))
    extrasettings = Column(Text)
    version = Column(String(75))
    size_ = Column(BigInteger)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)
    modifieddate = Column(DateTime)
    repositoryid = Column(BigInteger)
    fileentryid = Column(BigInteger, index=True)
    mimetype = Column(String(75), index=True)
    fileentrytypeid = Column(BigInteger)
    uuid_ = Column(String(75), index=True)
    treepath = Column(Text)
    checksum = Column(String(75))


class Dlfolder(Base):
    __tablename__ = 'dlfolder'
    __table_args__ = (
        Index('ix_ce360bf6', 'groupid', 'parentfolderid', 'hidden_', 'status'),
        Index('ix_51556082', 'parentfolderid', 'name'),
        Index('ix_902fd874', 'groupid', 'parentfolderid', 'name', unique=True),
        Index('ix_49c37475', 'groupid', 'parentfolderid'),
        Index('ix_da448450', 'uuid_', 'companyid'),
        Index('ix_3cc1ded2', 'uuid_', 'groupid', unique=True),
        Index('ix_c88430ab', 'groupid', 'mountpoint', 'parentfolderid', 'hidden_', 'status'),
        Index('ix_e79be432', 'companyid', 'status'),
        Index('ix_f78286c5', 'groupid', 'mountpoint', 'parentfolderid', 'hidden_'),
        Index('ix_2a048ea0', 'groupid', 'parentfolderid', 'mountpoint')
    )

    uuid_ = Column(String(75), index=True)
    folderid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    parentfolderid = Column(BigInteger)
    name = Column(String(120))
    description = Column(Text)
    lastpostdate = Column(DateTime)
    repositoryid = Column(BigInteger, index=True)
    mountpoint = Column(Boolean)
    defaultfileentrytypeid = Column(BigInteger)
    overridefileentrytypes = Column(Boolean)
    treepath = Column(Text)
    hidden_ = Column(Boolean)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Dlsyncevent(Base):
    __tablename__ = 'dlsyncevent'

    synceventid = Column(BigInteger, primary_key=True)
    modifiedtime = Column(BigInteger, index=True)
    event = Column(String(75))
    type_ = Column(String(75))
    typepk = Column(BigInteger, unique=True)


class Emailaddres(Base):
    __tablename__ = 'emailaddress'
    __table_args__ = (
        Index('ix_551a519f', 'companyid', 'classnameid', 'classpk'),
        Index('ix_2a2cb130', 'companyid', 'classnameid', 'classpk', 'primary_'),
        Index('ix_f74ab912', 'uuid_', 'companyid'),
        Index('ix_49d2dec4', 'companyid', 'classnameid')
    )

    emailaddressid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    address = Column(String(75))
    typeid = Column(Integer)
    primary_ = Column(Boolean)
    uuid_ = Column(String(75), index=True)


class Expandocolumn(Base):
    __tablename__ = 'expandocolumn'
    __table_args__ = (
        Index('ix_fefc8da7', 'tableid', 'name', unique=True),
    )

    columnid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    tableid = Column(BigInteger, index=True)
    name = Column(String(75))
    type_ = Column(Integer)
    defaultdata = Column(Text)
    typesettings = Column(Text)


class Expandorow(Base):
    __tablename__ = 'expandorow'
    __table_args__ = (
        Index('ix_81efbff5', 'tableid', 'classpk', unique=True),
    )

    rowid_ = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    tableid = Column(BigInteger, index=True)
    classpk = Column(BigInteger, index=True)
    modifieddate = Column(DateTime)


class Expandotable(Base):
    __tablename__ = 'expandotable'
    __table_args__ = (
        Index('ix_b5ae8a85', 'companyid', 'classnameid'),
        Index('ix_37562284', 'companyid', 'classnameid', 'name', unique=True)
    )

    tableid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    classnameid = Column(BigInteger)
    name = Column(String(75))


class Expandovalue(Base):
    __tablename__ = 'expandovalue'
    __table_args__ = (
        Index('ix_ca9afb7c', 'tableid', 'columnid'),
        Index('ix_9ddd21e5', 'columnid', 'rowid_', unique=True),
        Index('ix_1bd3f4c', 'tableid', 'classpk'),
        Index('ix_b29fef17', 'classnameid', 'classpk'),
        Index('ix_b71e92d5', 'tableid', 'rowid_'),
        Index('ix_d27b03e7', 'tableid', 'columnid', 'classpk', unique=True)
    )

    valueid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    tableid = Column(BigInteger, index=True)
    columnid = Column(BigInteger, index=True)
    rowid_ = Column(BigInteger, index=True)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    data_ = Column(Text)


class GeometryColumn(Base):
    __tablename__ = 'geometry_columns'

    f_table_catalog = Column(String(256), primary_key=True, nullable=False)
    f_table_schema = Column(String(256), primary_key=True, nullable=False)
    f_table_name = Column(String(256), primary_key=True, nullable=False)
    f_geometry_column = Column(String(256), primary_key=True, nullable=False)
    coord_dimension = Column(Integer, nullable=False)
    srid = Column(Integer, nullable=False)
    type = Column(String(30), nullable=False)


class Group(Base):
    __tablename__ = 'group_'
    __table_args__ = (
        Index('ix_d0d5e397', 'companyid', 'classnameid', 'classpk', unique=True),
        Index('ix_7b590a7a', 'type_', 'active_'),
        Index('ix_bbca55b', 'companyid', 'livegroupid', 'name', unique=True),
        Index('ix_5bddb872', 'companyid', 'friendlyurl', unique=True),
        Index('ix_6c499099', 'companyid', 'parentgroupid', 'site'),
        Index('ix_5d75499e', 'companyid', 'parentgroupid'),
        Index('ix_754fbb1c', 'uuid_', 'groupid', unique=True),
        Index('ix_abe2d54', 'companyid', 'classnameid', 'parentgroupid'),
        Index('ix_26cc761a', 'uuid_', 'companyid'),
        Index('ix_b584b5cc', 'companyid', 'classnameid'),
        Index('ix_5de0be11', 'companyid', 'classnameid', 'livegroupid', 'name', unique=True),
        Index('ix_5aa68501', 'companyid', 'name', unique=True),
        Index('ix_63a2aabd', 'companyid', 'site')
    )

    groupid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    creatoruserid = Column(BigInteger)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    parentgroupid = Column(BigInteger)
    livegroupid = Column(BigInteger, index=True)
    name = Column(String(150))
    description = Column(Text)
    type_ = Column(Integer)
    typesettings = Column(Text)
    friendlyurl = Column(String(255))
    active_ = Column(Boolean)
    site = Column(Boolean)
    uuid_ = Column(String(75), index=True)
    treepath = Column(Text)
    manualmembership = Column(Boolean)
    membershiprestriction = Column(Integer)
    remotestaginggroupcount = Column(Integer)


class GroupsOrg(Base):
    __tablename__ = 'groups_orgs'

    groupid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    organizationid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class GroupsRole(Base):
    __tablename__ = 'groups_roles'

    groupid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    roleid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class GroupsUsergroup(Base):
    __tablename__ = 'groups_usergroups'

    groupid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    usergroupid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class Image(Base):
    __tablename__ = 'image'

    imageid = Column(BigInteger, primary_key=True)
    modifieddate = Column(DateTime)
    type_ = Column(String(75))
    height = Column(Integer)
    width = Column(Integer)
    size_ = Column(Integer, index=True)


class Journalarticle(Base):
    __tablename__ = 'journalarticle'
    __table_args__ = (
        Index('ix_3c028c1e', 'groupid', 'layoutuuid'),
        Index('ix_451d63ec', 'resourceprimkey', 'indexable', 'status'),
        Index('ix_2e207659', 'groupid', 'structureid'),
        Index('ix_3d070845', 'companyid', 'version'),
        Index('ix_301d024b', 'groupid', 'status'),
        Index('ix_d19c1b9f', 'groupid', 'userid'),
        Index('ix_a2534ac2', 'groupid', 'classnameid', 'layoutuuid'),
        Index('ix_85c52eec', 'groupid', 'articleid', 'version', unique=True),
        Index('ix_68c0f69c', 'groupid', 'articleid'),
        Index('ix_f43b9ff2', 'groupid', 'classnameid', 'templateid'),
        Index('ix_3463d95b', 'uuid_', 'groupid', unique=True),
        Index('ix_4d5cd982', 'groupid', 'articleid', 'status'),
        Index('ix_f0a26b29', 'groupid', 'version', 'status'),
        Index('ix_ea05e9e1', 'displaydate', 'status'),
        Index('ix_22882d02', 'groupid', 'urltitle'),
        Index('ix_3e2765fc', 'resourceprimkey', 'status'),
        Index('ix_f35391e8', 'groupid', 'folderid', 'status'),
        Index('ix_43a0f80f', 'groupid', 'userid', 'classnameid'),
        Index('ix_71520099', 'uuid_', 'companyid'),
        Index('ix_d2d249e8', 'groupid', 'urltitle', 'status'),
        Index('ix_91e78c35', 'groupid', 'classnameid', 'structureid'),
        Index('ix_5cd17502', 'groupid', 'folderid'),
        Index('ix_8deae14e', 'groupid', 'templateid'),
        Index('ix_323df109', 'companyid', 'status'),
        Index('ix_9ce6e0fa', 'groupid', 'classnameid', 'classpk'),
        Index('ix_89ff8b06', 'resourceprimkey', 'indexable'),
        Index('ix_e82f322b', 'companyid', 'version', 'status')
    )

    uuid_ = Column(String(75), index=True)
    id_ = Column(BigInteger, primary_key=True)
    resourceprimkey = Column(BigInteger, index=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    articleid = Column(String(75))
    version = Column(Float(53))
    title = Column(Text)
    urltitle = Column(String(150))
    description = Column(Text)
    content = Column(Text)
    type_ = Column(String(75))
    structureid = Column(String(75), index=True)
    templateid = Column(String(75), index=True)
    displaydate = Column(DateTime)
    expirationdate = Column(DateTime)
    reviewdate = Column(DateTime)
    indexable = Column(Boolean)
    smallimage = Column(Boolean)
    smallimageid = Column(BigInteger, index=True)
    smallimageurl = Column(Text)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    layoutuuid = Column(String(75), index=True)
    folderid = Column(BigInteger)
    treepath = Column(Text)


class Journalarticleimage(Base):
    __tablename__ = 'journalarticleimage'
    __table_args__ = (
        Index('ix_103d6207', 'groupid', 'articleid', 'version', 'elinstanceid', 'elname', 'languageid', unique=True),
        Index('ix_158b526f', 'groupid', 'articleid', 'version')
    )

    articleimageid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    articleid = Column(String(75))
    version = Column(Float(53))
    elinstanceid = Column(String(75))
    elname = Column(String(75))
    languageid = Column(String(75))
    tempimage = Column(Boolean, index=True)


class Journalarticleresource(Base):
    __tablename__ = 'journalarticleresource'
    __table_args__ = (
        Index('ix_88df994a', 'groupid', 'articleid', unique=True),
        Index('ix_84ab0309', 'uuid_', 'groupid', unique=True)
    )

    resourceprimkey = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    articleid = Column(String(75))
    uuid_ = Column(String(75), index=True)


class Journalcontentsearch(Base):
    __tablename__ = 'journalcontentsearch'
    __table_args__ = (
        Index('ix_b3b318dc', 'groupid', 'privatelayout', 'layoutid'),
        Index('ix_7acc74c9', 'groupid', 'privatelayout', 'layoutid', 'portletid'),
        Index('ix_20962903', 'groupid', 'privatelayout'),
        Index('ix_c3aa93b8', 'groupid', 'privatelayout', 'layoutid', 'portletid', 'articleid', unique=True),
        Index('ix_7cc7d73e', 'groupid', 'privatelayout', 'articleid'),
        Index('ix_6838e427', 'groupid', 'articleid')
    )

    contentsearchid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    privatelayout = Column(Boolean)
    layoutid = Column(BigInteger)
    portletid = Column(String(200), index=True)
    articleid = Column(String(75), index=True)


class Journalfeed(Base):
    __tablename__ = 'journalfeed'
    __table_args__ = (
        Index('ix_65576cbc', 'groupid', 'feedid', unique=True),
        Index('ix_39031f51', 'uuid_', 'groupid', unique=True),
        Index('ix_cb37a10f', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    id_ = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    feedid = Column(String(75))
    name = Column(String(75))
    description = Column(Text)
    type_ = Column(String(75))
    structureid = Column(String(75))
    templateid = Column(String(75))
    renderertemplateid = Column(String(75))
    delta = Column(Integer)
    orderbycol = Column(String(75))
    orderbytype = Column(String(75))
    targetlayoutfriendlyurl = Column(String(255))
    targetportletid = Column(String(75))
    contentfield = Column(String(75))
    feedformat = Column(String(75))
    feedversion = Column(Float(53))


class Journalfolder(Base):
    __tablename__ = 'journalfolder'
    __table_args__ = (
        Index('ix_efd9cac', 'groupid', 'parentfolderid', 'status'),
        Index('ix_e988689e', 'groupid', 'name'),
        Index('ix_65026705', 'groupid', 'parentfolderid', 'name', unique=True),
        Index('ix_190483c6', 'groupid', 'parentfolderid'),
        Index('ix_e002061', 'uuid_', 'groupid', unique=True),
        Index('ix_54f89e1f', 'uuid_', 'companyid'),
        Index('ix_c36b0443', 'companyid', 'status')
    )

    uuid_ = Column(String(75), index=True)
    folderid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    parentfolderid = Column(BigInteger)
    treepath = Column(Text)
    name = Column(String(100))
    description = Column(Text)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Kaleoaction(Base):
    __tablename__ = 'kaleoaction'
    __table_args__ = (
        Index('ix_4b2545e8', 'kaleoclassname', 'kaleoclasspk', 'executiontype'),
        Index('ix_170efd7a', 'kaleoclassname', 'kaleoclasspk')
    )

    kaleoactionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleoclassname = Column(String(200))
    kaleoclasspk = Column(BigInteger)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleonodename = Column(String(200))
    name = Column(String(200))
    description = Column(Text)
    executiontype = Column(String(20))
    script = Column(Text)
    scriptlanguage = Column(String(75))
    scriptrequiredcontexts = Column(Text)
    priority = Column(Integer)


class Kaleocondition(Base):
    __tablename__ = 'kaleocondition'

    kaleoconditionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleonodeid = Column(BigInteger, index=True)
    script = Column(Text)
    scriptlanguage = Column(String(75))
    scriptrequiredcontexts = Column(String(75))


class Kaleodefinition(Base):
    __tablename__ = 'kaleodefinition'
    __table_args__ = (
        Index('ix_ec14f81a', 'companyid', 'name', 'version'),
        Index('ix_4c23f11b', 'companyid', 'name', 'active_'),
        Index('ix_408542ba', 'companyid', 'active_'),
        Index('ix_76c781ae', 'companyid', 'name')
    )

    kaleodefinitionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(200))
    title = Column(Text)
    description = Column(Text)
    content = Column(Text)
    version = Column(Integer)
    active_ = Column(Boolean)
    startkaleonodeid = Column(BigInteger)


class Kaleoinstance(Base):
    __tablename__ = 'kaleoinstance'
    __table_args__ = (
        Index('ix_bf5839f8', 'companyid', 'kaleodefinitionname', 'kaleodefinitionversion', 'completiondate'),
        Index('ix_acf16238', 'kaleodefinitionid', 'completed')
    )

    kaleoinstanceid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleodefinitionname = Column(String(200))
    kaleodefinitionversion = Column(Integer)
    rootkaleoinstancetokenid = Column(BigInteger)
    classname = Column(String(200))
    classpk = Column(BigInteger)
    completed = Column(Boolean)
    completiondate = Column(DateTime)
    workflowcontext = Column(Text)


class Kaleoinstancetoken(Base):
    __tablename__ = 'kaleoinstancetoken'
    __table_args__ = (
        Index('ix_4a86923b', 'companyid', 'parentkaleoinstancetokenid'),
        Index('ix_360d34d9', 'companyid', 'parentkaleoinstancetokenid', 'completiondate')
    )

    kaleoinstancetokenid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleoinstanceid = Column(BigInteger, index=True)
    parentkaleoinstancetokenid = Column(BigInteger)
    currentkaleonodeid = Column(BigInteger)
    currentkaleonodename = Column(String(200))
    classname = Column(String(200))
    classpk = Column(BigInteger)
    completed = Column(Boolean)
    completiondate = Column(DateTime)


class Kaleolog(Base):
    __tablename__ = 'kaleolog'
    __table_args__ = (
        Index('ix_e66a153a', 'kaleoclassname', 'kaleoclasspk', 'kaleoinstancetokenid', 'type_'),
        Index('ix_470b9ff8', 'kaleoinstancetokenid', 'type_')
    )

    kaleologid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleoclassname = Column(String(200))
    kaleoclasspk = Column(BigInteger)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleoinstanceid = Column(BigInteger, index=True)
    kaleoinstancetokenid = Column(BigInteger)
    kaleotaskinstancetokenid = Column(BigInteger, index=True)
    kaleonodename = Column(String(200))
    terminalkaleonode = Column(Boolean)
    kaleoactionid = Column(BigInteger)
    kaleoactionname = Column(String(200))
    kaleoactiondescription = Column(Text)
    previouskaleonodeid = Column(BigInteger)
    previouskaleonodename = Column(String(200))
    previousassigneeclassname = Column(String(200))
    previousassigneeclasspk = Column(BigInteger)
    currentassigneeclassname = Column(String(200))
    currentassigneeclasspk = Column(BigInteger)
    type_ = Column(String(50))
    comment_ = Column(Text)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    duration = Column(BigInteger)
    workflowcontext = Column(Text)


class Kaleonode(Base):
    __tablename__ = 'kaleonode'
    __table_args__ = (
        Index('ix_f28c443e', 'companyid', 'kaleodefinitionid'),
    )

    kaleonodeid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleodefinitionid = Column(BigInteger, index=True)
    name = Column(String(200))
    metadata_ = Column('metadata', Text)
    description = Column(Text)
    type_ = Column(String(20))
    initial_ = Column(Boolean)
    terminal = Column(Boolean)


class Kaleonotification(Base):
    __tablename__ = 'kaleonotification'
    __table_args__ = (
        Index('ix_902d342f', 'kaleoclassname', 'kaleoclasspk'),
        Index('ix_f3362e93', 'kaleoclassname', 'kaleoclasspk', 'executiontype')
    )

    kaleonotificationid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleoclassname = Column(String(200))
    kaleoclasspk = Column(BigInteger)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleonodename = Column(String(200))
    name = Column(String(200))
    description = Column(Text)
    executiontype = Column(String(20))
    template = Column(Text)
    templatelanguage = Column(String(75))
    notificationtypes = Column(String(25))


class Kaleonotificationrecipient(Base):
    __tablename__ = 'kaleonotificationrecipient'

    kaleonotificationrecipientid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleonotificationid = Column(BigInteger, index=True)
    recipientclassname = Column(String(200))
    recipientclasspk = Column(BigInteger)
    recipientroletype = Column(Integer)
    address = Column(String(255))


class Kaleotask(Base):
    __tablename__ = 'kaleotask'

    kaleotaskid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleonodeid = Column(BigInteger, index=True)
    name = Column(String(200))
    description = Column(Text)


class Kaleotaskassignment(Base):
    __tablename__ = 'kaleotaskassignment'
    __table_args__ = (
        Index('ix_1087068e', 'kaleoclassname', 'kaleoclasspk', 'assigneeclassname'),
        Index('ix_d835c576', 'kaleoclassname', 'kaleoclasspk')
    )

    kaleotaskassignmentid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleoclassname = Column(String(200))
    kaleoclasspk = Column(BigInteger)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleonodeid = Column(BigInteger)
    assigneeclassname = Column(String(200))
    assigneeclasspk = Column(BigInteger)
    assigneeactionid = Column(String(75))
    assigneescript = Column(Text)
    assigneescriptlanguage = Column(String(75))
    assigneescriptrequiredcontexts = Column(String(75))


class Kaleotaskassignmentinstance(Base):
    __tablename__ = 'kaleotaskassignmentinstance'

    kaleotaskassignmentinstanceid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleoinstanceid = Column(BigInteger, index=True)
    kaleoinstancetokenid = Column(BigInteger)
    kaleotaskinstancetokenid = Column(BigInteger, index=True)
    kaleotaskid = Column(BigInteger)
    kaleotaskname = Column(String(200))
    assigneeclassname = Column(String(200))
    assigneeclasspk = Column(BigInteger)
    completed = Column(Boolean)
    completiondate = Column(DateTime)


class Kaleotaskinstancetoken(Base):
    __tablename__ = 'kaleotaskinstancetoken'
    __table_args__ = (
        Index('ix_b857a115', 'kaleoinstanceid', 'kaleotaskid'),
    )

    kaleotaskinstancetokenid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleoinstanceid = Column(BigInteger, index=True)
    kaleoinstancetokenid = Column(BigInteger)
    kaleotaskid = Column(BigInteger)
    kaleotaskname = Column(String(200))
    classname = Column(String(200))
    classpk = Column(BigInteger)
    completionuserid = Column(BigInteger)
    completed = Column(Boolean)
    completiondate = Column(DateTime)
    duedate = Column(DateTime)
    workflowcontext = Column(Text)


class Kaleotimer(Base):
    __tablename__ = 'kaleotimer'
    __table_args__ = (
        Index('ix_1a479f32', 'kaleoclassname', 'kaleoclasspk', 'blocking'),
        Index('ix_4de6a889', 'kaleoclassname', 'kaleoclasspk')
    )

    kaleotimerid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleoclassname = Column(String(200))
    kaleoclasspk = Column(BigInteger)
    kaleodefinitionid = Column(BigInteger)
    name = Column(String(75))
    blocking = Column(Boolean)
    description = Column(Text)
    duration = Column(Float(53))
    scale = Column(String(75))
    recurrenceduration = Column(Float(53))
    recurrencescale = Column(String(75))


class Kaleotimerinstancetoken(Base):
    __tablename__ = 'kaleotimerinstancetoken'
    __table_args__ = (
        Index('ix_9932524c', 'kaleoinstancetokenid', 'completed', 'blocking'),
        Index('ix_13a5ba2c', 'kaleoinstancetokenid', 'kaleotimerid'),
        Index('ix_db279423', 'kaleoinstancetokenid', 'completed')
    )

    kaleotimerinstancetokenid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleoclassname = Column(String(200))
    kaleoclasspk = Column(BigInteger)
    kaleodefinitionid = Column(BigInteger)
    kaleoinstanceid = Column(BigInteger, index=True)
    kaleoinstancetokenid = Column(BigInteger)
    kaleotaskinstancetokenid = Column(BigInteger)
    kaleotimerid = Column(BigInteger)
    kaleotimername = Column(String(200))
    blocking = Column(Boolean)
    completionuserid = Column(BigInteger)
    completed = Column(Boolean)
    completiondate = Column(DateTime)
    workflowcontext = Column(Text)


class Kaleotransition(Base):
    __tablename__ = 'kaleotransition'
    __table_args__ = (
        Index('ix_a38e2194', 'kaleonodeid', 'defaulttransition'),
        Index('ix_85268a11', 'kaleonodeid', 'name')
    )

    kaleotransitionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(200))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    kaleodefinitionid = Column(BigInteger, index=True)
    kaleonodeid = Column(BigInteger, index=True)
    name = Column(String(200))
    description = Column(Text)
    sourcekaleonodeid = Column(BigInteger)
    sourcekaleonodename = Column(String(200))
    targetkaleonodeid = Column(BigInteger)
    targetkaleonodename = Column(String(200))
    defaulttransition = Column(Boolean)


class Layout(Base):
    __tablename__ = 'layout'
    __table_args__ = (
        Index('ix_e118c537', 'uuid_', 'groupid', 'privatelayout', unique=True),
        Index('ix_bc2c4231', 'groupid', 'privatelayout', 'friendlyurl', unique=True),
        Index('ix_1a1b61d2', 'groupid', 'privatelayout', 'type_'),
        Index('ix_ced31606', 'uuid_', 'groupid', unique=True),
        Index('ix_2ce4be84', 'uuid_', 'companyid'),
        Index('ix_7162c27c', 'groupid', 'privatelayout', 'layoutid', unique=True),
        Index('ix_8ce8c0d9', 'groupid', 'privatelayout', 'sourceprototypelayoutuuid'),
        Index('ix_705f5aa3', 'groupid', 'privatelayout'),
        Index('ix_6de88b06', 'groupid', 'privatelayout', 'parentlayoutid')
    )

    uuid_ = Column(String(75), index=True)
    plid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    privatelayout = Column(Boolean)
    layoutid = Column(BigInteger)
    parentlayoutid = Column(BigInteger)
    name = Column(Text)
    title = Column(Text)
    description = Column(Text)
    type_ = Column(String(75))
    typesettings = Column(Text)
    hidden_ = Column(Boolean)
    friendlyurl = Column(String(255))
    iconimage = Column(Boolean)
    iconimageid = Column(BigInteger, index=True)
    themeid = Column(String(75))
    colorschemeid = Column(String(75))
    wapthemeid = Column(String(75))
    wapcolorschemeid = Column(String(75))
    css = Column(Text)
    priority = Column(Integer)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    keywords = Column(Text)
    robots = Column(Text)
    layoutprototypeuuid = Column(String(75), index=True)
    layoutprototypelinkenabled = Column(Boolean)
    sourceprototypelayoutuuid = Column(String(75), index=True)
    userid = Column(BigInteger)
    username = Column(String(75))


class Layoutbranch(Base):
    __tablename__ = 'layoutbranch'
    __table_args__ = (
        Index('ix_a705ff94', 'layoutsetbranchid', 'plid', 'master'),
        Index('ix_2c42603e', 'layoutsetbranchid', 'plid'),
        Index('ix_fd57097d', 'layoutsetbranchid', 'plid', 'name', unique=True)
    )

    layoutbranchid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    layoutsetbranchid = Column(BigInteger, index=True)
    plid = Column(BigInteger)
    name = Column(String(75))
    description = Column(Text)
    master = Column(Boolean)


class Layoutfriendlyurl(Base):
    __tablename__ = 'layoutfriendlyurl'
    __table_args__ = (
        Index('ix_326525d6', 'uuid_', 'groupid', unique=True),
        Index('ix_ca713461', 'groupid', 'privatelayout', 'friendlyurl'),
        Index('ix_f4321a54', 'uuid_', 'companyid'),
        Index('ix_c5762e72', 'plid', 'languageid', unique=True),
        Index('ix_59051329', 'plid', 'friendlyurl'),
        Index('ix_a6fc2b28', 'groupid', 'privatelayout', 'friendlyurl', 'languageid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    layoutfriendlyurlid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    plid = Column(BigInteger, index=True)
    privatelayout = Column(Boolean)
    friendlyurl = Column(String(255))
    languageid = Column(String(75))


class Layoutprototype(Base):
    __tablename__ = 'layoutprototype'
    __table_args__ = (
        Index('ix_63ed2532', 'uuid_', 'companyid'),
        Index('ix_557a639f', 'companyid', 'active_')
    )

    layoutprototypeid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    name = Column(Text)
    description = Column(Text)
    settings_ = Column(Text)
    active_ = Column(Boolean)
    uuid_ = Column(String(75), index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)


class Layoutrevision(Base):
    __tablename__ = 'layoutrevision'
    __table_args__ = (
        Index('ix_a9ac086e', 'layoutsetbranchid', 'head'),
        Index('ix_70da9ecb', 'layoutsetbranchid', 'plid', 'status'),
        Index('ix_4a84af43', 'layoutsetbranchid', 'parentlayoutrevisionid', 'plid'),
        Index('ix_7ffae700', 'layoutsetbranchid', 'status'),
        Index('ix_13984800', 'layoutsetbranchid', 'layoutbranchid', 'plid'),
        Index('ix_e10ac39', 'layoutsetbranchid', 'head', 'plid'),
        Index('ix_8ec3d2bc', 'plid', 'status'),
        Index('ix_43e8286a', 'head', 'plid'),
        Index('ix_b7b914e5', 'layoutsetbranchid', 'plid')
    )

    layoutrevisionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    layoutsetbranchid = Column(BigInteger, index=True)
    layoutbranchid = Column(BigInteger)
    parentlayoutrevisionid = Column(BigInteger)
    head = Column(Boolean)
    major = Column(Boolean)
    plid = Column(BigInteger, index=True)
    privatelayout = Column(Boolean)
    name = Column(Text)
    title = Column(Text)
    description = Column(Text)
    keywords = Column(Text)
    robots = Column(Text)
    typesettings = Column(Text)
    iconimage = Column(Boolean)
    iconimageid = Column(BigInteger)
    themeid = Column(String(75))
    colorschemeid = Column(String(75))
    wapthemeid = Column(String(75))
    wapcolorschemeid = Column(String(75))
    css = Column(Text)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Layoutset(Base):
    __tablename__ = 'layoutset'
    __table_args__ = (
        Index('ix_48550691', 'groupid', 'privatelayout', unique=True),
    )

    layoutsetid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    privatelayout = Column(Boolean)
    logo = Column(Boolean)
    logoid = Column(BigInteger)
    themeid = Column(String(75))
    colorschemeid = Column(String(75))
    wapthemeid = Column(String(75))
    wapcolorschemeid = Column(String(75))
    css = Column(Text)
    pagecount = Column(Integer)
    settings_ = Column(Text)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    layoutsetprototypeuuid = Column(String(75), index=True)
    layoutsetprototypelinkenabled = Column(Boolean)


class Layoutsetbranch(Base):
    __tablename__ = 'layoutsetbranch'
    __table_args__ = (
        Index('ix_c4079fd3', 'groupid', 'privatelayout'),
        Index('ix_ccf0da29', 'groupid', 'privatelayout', 'master'),
        Index('ix_5ff18552', 'groupid', 'privatelayout', 'name', unique=True)
    )

    layoutsetbranchid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    privatelayout = Column(Boolean)
    name = Column(String(75))
    description = Column(Text)
    master = Column(Boolean)
    logo = Column(Boolean)
    logoid = Column(BigInteger)
    themeid = Column(String(75))
    colorschemeid = Column(String(75))
    wapthemeid = Column(String(75))
    wapcolorschemeid = Column(String(75))
    css = Column(Text)
    settings_ = Column(Text)
    layoutsetprototypeuuid = Column(String(75))
    layoutsetprototypelinkenabled = Column(Boolean)


class Layoutsetprototype(Base):
    __tablename__ = 'layoutsetprototype'
    __table_args__ = (
        Index('ix_9178fc71', 'companyid', 'active_'),
        Index('ix_d9ffca84', 'uuid_', 'companyid')
    )

    layoutsetprototypeid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    name = Column(Text)
    description = Column(Text)
    settings_ = Column(Text)
    active_ = Column(Boolean)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    uuid_ = Column(String(75), index=True)
    userid = Column(BigInteger)
    username = Column(String(75))


class LibraryBook(Base):
    __tablename__ = 'library_book'

    bookid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    groupid = Column(BigInteger, index=True)
    publisherid = Column(BigInteger, index=True)
    title = Column(Text)
    authorname = Column(String(75))
    publicationdate = Column(DateTime)


class LibraryPublisher(Base):
    __tablename__ = 'library_publisher'

    publisherid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    groupid = Column(BigInteger, index=True)
    name = Column(String(75))
    emailaddress = Column(String(75))
    website = Column(String(75))
    phonenumber = Column(String(75))
    country = Column(String(75))


class Listtype(Base):
    __tablename__ = 'listtype'

    listtypeid = Column(Integer, primary_key=True)
    name = Column(String(75))
    type_ = Column(String(75), index=True)


class Lock(Base):
    __tablename__ = 'lock_'
    __table_args__ = (
        Index('ix_228562ad', 'classname', 'key_', unique=True),
        Index('ix_2c418eae', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    lockid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    classname = Column(String(75))
    key_ = Column(String(200))
    owner = Column(String(300))
    inheritable = Column(Boolean)
    expirationdate = Column(DateTime, index=True)


class MailAccount(Base):
    __tablename__ = 'mail_account'
    __table_args__ = (
        Index('ix_6b92f85f', 'userid', 'address'),
    )

    accountid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    address = Column(String(75))
    personalname = Column(String(75))
    protocol = Column(String(75))
    incominghostname = Column(String(75))
    incomingport = Column(Integer)
    incomingsecure = Column(Boolean)
    outgoinghostname = Column(String(75))
    outgoingport = Column(Integer)
    outgoingsecure = Column(Boolean)
    login = Column(String(75))
    password_ = Column(String(75))
    savepassword = Column(Boolean)
    signature = Column(String(75))
    usesignature = Column(Boolean)
    folderprefix = Column(String(75))
    inboxfolderid = Column(BigInteger)
    draftfolderid = Column(BigInteger)
    sentfolderid = Column(BigInteger)
    trashfolderid = Column(BigInteger)
    defaultsender = Column(Boolean)


class MailAttachment(Base):
    __tablename__ = 'mail_attachment'

    attachmentid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    accountid = Column(BigInteger)
    folderid = Column(BigInteger)
    messageid = Column(BigInteger, index=True)
    contentpath = Column(String(75))
    filename = Column(String(75))
    size_ = Column(BigInteger)


class MailFolder(Base):
    __tablename__ = 'mail_folder'
    __table_args__ = (
        Index('ix_310e554a', 'accountid', 'fullname'),
    )

    folderid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    accountid = Column(BigInteger, index=True)
    fullname = Column(String(75))
    displayname = Column(String(75))
    remotemessagecount = Column(Integer)


class MailMessage(Base):
    __tablename__ = 'mail_message'
    __table_args__ = (
        Index('ix_200d262a', 'folderid', 'remotemessageid'),
    )

    messageid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    accountid = Column(BigInteger)
    folderid = Column(BigInteger, index=True)
    sender = Column(Text)
    to_ = Column(Text)
    cc = Column(Text)
    bcc = Column(Text)
    sentdate = Column(DateTime)
    subject = Column(Text)
    preview = Column(String(75))
    body = Column(Text)
    flags = Column(String(75))
    size_ = Column(BigInteger)
    remotemessageid = Column(BigInteger)


class MarketplaceApp(Base):
    __tablename__ = 'marketplace_app'
    __table_args__ = (
        Index('ix_a7807da7', 'uuid_', 'companyid'),
    )

    uuid_ = Column(String(75), index=True)
    appid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    remoteappid = Column(BigInteger, index=True)
    title = Column(String(75))
    description = Column(Text)
    category = Column(String(75), index=True)
    iconurl = Column(Text)
    version = Column(String(75))


class MarketplaceModule(Base):
    __tablename__ = 'marketplace_module'
    __table_args__ = (
        Index('ix_c6938724', 'appid', 'contextname'),
    )

    uuid_ = Column(String(75), index=True)
    moduleid = Column(BigInteger, primary_key=True)
    appid = Column(BigInteger, index=True)
    contextname = Column(String(75), index=True)


class Mbban(Base):
    __tablename__ = 'mbban'
    __table_args__ = (
        Index('ix_8abc4e3b', 'groupid', 'banuserid', unique=True),
        Index('ix_2a3b68f6', 'uuid_', 'groupid', unique=True),
        Index('ix_4f841574', 'uuid_', 'companyid')
    )

    banid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    banuserid = Column(BigInteger, index=True)
    uuid_ = Column(String(75), index=True)


class Mbcategory(Base):
    __tablename__ = 'mbcategory'
    __table_args__ = (
        Index('ix_13df4e6d', 'uuid_', 'companyid'),
        Index('ix_da84a9f7', 'groupid', 'status'),
        Index('ix_e15a5db5', 'companyid', 'status'),
        Index('ix_f7d28c2f', 'uuid_', 'groupid', unique=True),
        Index('ix_c295dbee', 'groupid', 'parentcategoryid', 'status'),
        Index('ix_ed292508', 'groupid', 'parentcategoryid')
    )

    uuid_ = Column(String(75), index=True)
    categoryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    parentcategoryid = Column(BigInteger)
    name = Column(String(75))
    description = Column(Text)
    threadcount = Column(Integer)
    messagecount = Column(Integer)
    lastpostdate = Column(DateTime)
    displaystyle = Column(String(75))
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Mbdiscussion(Base):
    __tablename__ = 'mbdiscussion'
    __table_args__ = (
        Index('ix_33a4de38', 'classnameid', 'classpk', unique=True),
        Index('ix_7e965757', 'uuid_', 'companyid'),
        Index('ix_f7aac799', 'uuid_', 'groupid', unique=True)
    )

    discussionid = Column(BigInteger, primary_key=True)
    classnameid = Column(BigInteger, index=True)
    classpk = Column(BigInteger)
    threadid = Column(BigInteger, unique=True)
    uuid_ = Column(String(75), index=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)


class Mbmailinglist(Base):
    __tablename__ = 'mbmailinglist'
    __table_args__ = (
        Index('ix_e858f170', 'uuid_', 'groupid', unique=True),
        Index('ix_fc61676e', 'uuid_', 'companyid'),
        Index('ix_76ce9cdd', 'groupid', 'categoryid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    mailinglistid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    categoryid = Column(BigInteger)
    emailaddress = Column(String(75))
    inprotocol = Column(String(75))
    inservername = Column(String(75))
    inserverport = Column(Integer)
    inusessl = Column(Boolean)
    inusername = Column(String(75))
    inpassword = Column(String(75))
    inreadinterval = Column(Integer)
    outemailaddress = Column(String(75))
    outcustom = Column(Boolean)
    outservername = Column(String(75))
    outserverport = Column(Integer)
    outusessl = Column(Boolean)
    outusername = Column(String(75))
    outpassword = Column(String(75))
    active_ = Column(Boolean, index=True)
    allowanonymous = Column(Boolean)


class Mbmessage(Base):
    __tablename__ = 'mbmessage'
    __table_args__ = (
        Index('ix_57ca9fec', 'uuid_', 'companyid'),
        Index('ix_9dc8e57', 'threadid', 'status'),
        Index('ix_9d7c3b23', 'threadid', 'answer'),
        Index('ix_8eb8c5ec', 'groupid', 'userid'),
        Index('ix_1ad93c16', 'companyid', 'status'),
        Index('ix_8d12316e', 'uuid_', 'groupid', unique=True),
        Index('ix_51a8d44d', 'classnameid', 'classpk'),
        Index('ix_4a4bb4ed', 'userid', 'classnameid', 'classpk', 'status'),
        Index('ix_f6687633', 'classnameid', 'classpk', 'status'),
        Index('ix_377858d2', 'groupid', 'userid', 'status'),
        Index('ix_3321f142', 'userid', 'classnameid', 'status'),
        Index('ix_59f9ce5c', 'userid', 'classnameid'),
        Index('ix_1073ab9f', 'groupid', 'categoryid'),
        Index('ix_4257db85', 'groupid', 'categoryid', 'status'),
        Index('ix_385e123e', 'groupid', 'categoryid', 'threadid', 'status'),
        Index('ix_abeb6d07', 'userid', 'classnameid', 'classpk'),
        Index('ix_a7038cd7', 'threadid', 'parentmessageid'),
        Index('ix_cbfdbf0a', 'groupid', 'categoryid', 'threadid', 'answer'),
        Index('ix_ed39ac98', 'groupid', 'status'),
        Index('ix_b674ab58', 'groupid', 'categoryid', 'threadid')
    )

    uuid_ = Column(String(75), index=True)
    messageid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    categoryid = Column(BigInteger)
    threadid = Column(BigInteger, index=True)
    rootmessageid = Column(BigInteger)
    parentmessageid = Column(BigInteger)
    subject = Column(String(75))
    body = Column(Text)
    anonymous = Column(Boolean)
    priority = Column(Float(53))
    allowpingbacks = Column(Boolean)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)
    format = Column(String(75))
    answer = Column(Boolean)


class Mbstatsuser(Base):
    __tablename__ = 'mbstatsuser'
    __table_args__ = (
        Index('ix_9168e2c9', 'groupid', 'userid', unique=True),
        Index('ix_d33a5445', 'groupid', 'userid', 'messagecount'),
        Index('ix_fab5a88b', 'groupid', 'messagecount')
    )

    statsuserid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    messagecount = Column(Integer)
    lastpostdate = Column(DateTime)


class Mbthread(Base):
    __tablename__ = 'mbthread'
    __table_args__ = (
        Index('ix_41f6dc8a', 'categoryid', 'priority'),
        Index('ix_f8ca2ab9', 'uuid_', 'companyid'),
        Index('ix_9a2d11b2', 'groupid', 'categoryid'),
        Index('ix_3a200b7b', 'uuid_', 'groupid', unique=True),
        Index('ix_e1e7142b', 'groupid', 'status'),
        Index('ix_aedd9cb5', 'lastpostdate', 'priority'),
        Index('ix_50f1904a', 'groupid', 'categoryid', 'lastpostdate'),
        Index('ix_485f7e98', 'groupid', 'categoryid', 'status')
    )

    threadid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    categoryid = Column(BigInteger)
    rootmessageid = Column(BigInteger, index=True)
    messagecount = Column(Integer)
    viewcount = Column(Integer)
    lastpostbyuserid = Column(BigInteger)
    lastpostdate = Column(DateTime)
    priority = Column(Float(53))
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)
    companyid = Column(BigInteger)
    rootmessageuserid = Column(BigInteger)
    question = Column(Boolean)
    uuid_ = Column(String(75), index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)


class Mbthreadflag(Base):
    __tablename__ = 'mbthreadflag'
    __table_args__ = (
        Index('ix_33781904', 'userid', 'threadid'),
        Index('ix_dce308c5', 'uuid_', 'companyid'),
        Index('ix_feb0fc87', 'uuid_', 'groupid', unique=True)
    )

    threadflagid = Column(BigInteger, primary_key=True)
    userid = Column(BigInteger, index=True)
    modifieddate = Column(DateTime)
    threadid = Column(BigInteger, index=True)
    uuid_ = Column(String(75), index=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)


class Mdraction(Base):
    __tablename__ = 'mdraction'
    __table_args__ = (
        Index('ix_c58a516b', 'uuid_', 'companyid'),
        Index('ix_75be36ad', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    actionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    rulegroupinstanceid = Column(BigInteger, index=True)
    name = Column(Text)
    description = Column(Text)
    type_ = Column(String(255))
    typesettings = Column(Text)


class Mdrrule(Base):
    __tablename__ = 'mdrrule'
    __table_args__ = (
        Index('ix_f3efdcb3', 'uuid_', 'groupid', unique=True),
        Index('ix_7dea8df1', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    ruleid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    rulegroupid = Column(BigInteger, index=True)
    name = Column(Text)
    description = Column(Text)
    type_ = Column(String(255))
    typesettings = Column(Text)


class Mdrrulegroup(Base):
    __tablename__ = 'mdrrulegroup'
    __table_args__ = (
        Index('ix_cc14dc2', 'uuid_', 'companyid'),
        Index('ix_46665cc4', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    rulegroupid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(Text)
    description = Column(Text)


class Mdrrulegroupinstance(Base):
    __tablename__ = 'mdrrulegroupinstance'
    __table_args__ = (
        Index('ix_22dab85c', 'groupid', 'classnameid', 'classpk'),
        Index('ix_9cbc6a39', 'uuid_', 'groupid', unique=True),
        Index('ix_808a0036', 'classnameid', 'classpk', 'rulegroupid', unique=True),
        Index('ix_25c9d1f7', 'uuid_', 'companyid'),
        Index('ix_c95a08d8', 'classnameid', 'classpk')
    )

    uuid_ = Column(String(75), index=True)
    rulegroupinstanceid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    rulegroupid = Column(BigInteger, index=True)
    priority = Column(Integer)


class Membershiprequest(Base):
    __tablename__ = 'membershiprequest'
    __table_args__ = (
        Index('ix_35aa8fa6', 'groupid', 'userid', 'statusid'),
        Index('ix_c28c72ec', 'groupid', 'statusid')
    )

    membershiprequestid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    createdate = Column(DateTime)
    groupid = Column(BigInteger, index=True)
    comments = Column(Text)
    replycomments = Column(Text)
    replydate = Column(DateTime)
    replieruserid = Column(BigInteger)
    statusid = Column(Integer)


class OpensocialGadget(Base):
    __tablename__ = 'opensocial_gadget'
    __table_args__ = (
        Index('ix_a6a89eb1', 'companyid', 'url', unique=True),
        Index('ix_3c79316e', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    gadgetid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    url = Column(Text)
    portletcategorynames = Column(Text)


class OpensocialOauthconsumer(Base):
    __tablename__ = 'opensocial_oauthconsumer'
    __table_args__ = (
        Index('ix_8e715bf8', 'gadgetkey', 'servicename'),
    )

    oauthconsumerid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    gadgetkey = Column(String(75), index=True)
    servicename = Column(String(75))
    consumerkey = Column(String(75))
    consumersecret = Column(Text)
    keytype = Column(String(75))


class OpensocialOauthtoken(Base):
    __tablename__ = 'opensocial_oauthtoken'
    __table_args__ = (
        Index('ix_6c8ccc3d', 'gadgetkey', 'servicename'),
        Index('ix_cdd35402', 'userid', 'gadgetkey', 'servicename', 'moduleid', 'tokenname')
    )

    oauthtokenid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    gadgetkey = Column(String(75))
    servicename = Column(String(75))
    moduleid = Column(BigInteger)
    accesstoken = Column(String(75))
    tokenname = Column(String(75))
    tokensecret = Column(String(75))
    sessionhandle = Column(String(75))
    expiration = Column(BigInteger)


class Organization(Base):
    __tablename__ = 'organization_'
    __table_args__ = (
        Index('ix_418e4522', 'companyid', 'parentorganizationid'),
        Index('ix_e301bdf5', 'companyid', 'name', unique=True),
        Index('ix_a9d85ba6', 'uuid_', 'companyid')
    )

    organizationid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    parentorganizationid = Column(BigInteger)
    name = Column(String(100))
    type_ = Column(String(75))
    recursable = Column(Boolean)
    regionid = Column(BigInteger)
    countryid = Column(BigInteger)
    statusid = Column(Integer)
    comments = Column(Text)
    treepath = Column(Text)
    uuid_ = Column(String(75), index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)


class Orggrouprole(Base):
    __tablename__ = 'orggrouprole'

    organizationid = Column(BigInteger, primary_key=True, nullable=False)
    groupid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    roleid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class Orglabor(Base):
    __tablename__ = 'orglabor'

    orglaborid = Column(BigInteger, primary_key=True)
    organizationid = Column(BigInteger, index=True)
    typeid = Column(Integer)
    sunopen = Column(Integer)
    sunclose = Column(Integer)
    monopen = Column(Integer)
    monclose = Column(Integer)
    tueopen = Column(Integer)
    tueclose = Column(Integer)
    wedopen = Column(Integer)
    wedclose = Column(Integer)
    thuopen = Column(Integer)
    thuclose = Column(Integer)
    friopen = Column(Integer)
    friclose = Column(Integer)
    satopen = Column(Integer)
    satclose = Column(Integer)


class Passwordpolicy(Base):
    __tablename__ = 'passwordpolicy'
    __table_args__ = (
        Index('ix_2c1142e', 'companyid', 'defaultpolicy'),
        Index('ix_3fbfa9f4', 'companyid', 'name', unique=True),
        Index('ix_e4d7ef87', 'uuid_', 'companyid')
    )

    passwordpolicyid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    defaultpolicy = Column(Boolean)
    name = Column(String(75))
    description = Column(Text)
    changeable = Column(Boolean)
    changerequired = Column(Boolean)
    minage = Column(BigInteger)
    checksyntax = Column(Boolean)
    allowdictionarywords = Column(Boolean)
    minalphanumeric = Column(Integer)
    minlength = Column(Integer)
    minlowercase = Column(Integer)
    minnumbers = Column(Integer)
    minsymbols = Column(Integer)
    minuppercase = Column(Integer)
    history = Column(Boolean)
    historycount = Column(Integer)
    expireable = Column(Boolean)
    maxage = Column(BigInteger)
    warningtime = Column(BigInteger)
    gracelimit = Column(Integer)
    lockout = Column(Boolean)
    maxfailure = Column(Integer)
    lockoutduration = Column(BigInteger)
    requireunlock = Column(Boolean)
    resetfailurecount = Column(BigInteger)
    resetticketmaxage = Column(BigInteger)
    uuid_ = Column(String(75), index=True)
    regex = Column(String(75))


class Passwordpolicyrel(Base):
    __tablename__ = 'passwordpolicyrel'
    __table_args__ = (
        Index('ix_c3a17327', 'classnameid', 'classpk', unique=True),
    )

    passwordpolicyrelid = Column(BigInteger, primary_key=True)
    passwordpolicyid = Column(BigInteger, index=True)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)


class Passwordtracker(Base):
    __tablename__ = 'passwordtracker'

    passwordtrackerid = Column(BigInteger, primary_key=True)
    userid = Column(BigInteger, index=True)
    createdate = Column(DateTime)
    password_ = Column(String(75))


class Phone(Base):
    __tablename__ = 'phone'
    __table_args__ = (
        Index('ix_b271fa88', 'uuid_', 'companyid'),
        Index('ix_812ce07a', 'companyid', 'classnameid', 'classpk', 'primary_'),
        Index('ix_9a53569', 'companyid', 'classnameid', 'classpk'),
        Index('ix_a2e4afba', 'companyid', 'classnameid')
    )

    phoneid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    number_ = Column(String(75))
    extension = Column(String(75))
    typeid = Column(Integer)
    primary_ = Column(Boolean)
    uuid_ = Column(String(75), index=True)


class Pluginsetting(Base):
    __tablename__ = 'pluginsetting'
    __table_args__ = (
        Index('ix_7171b2e8', 'companyid', 'pluginid', 'plugintype', unique=True),
    )

    pluginsettingid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    pluginid = Column(String(75))
    plugintype = Column(String(75))
    roles = Column(Text)
    active_ = Column(Boolean)


class Pollschoice(Base):
    __tablename__ = 'pollschoice'
    __table_args__ = (
        Index('ix_c222bd31', 'uuid_', 'groupid', unique=True),
        Index('ix_d76dd2cf', 'questionid', 'name', unique=True),
        Index('ix_8ae746ef', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    choiceid = Column(BigInteger, primary_key=True)
    questionid = Column(BigInteger, index=True)
    name = Column(String(75))
    description = Column(Text)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)


class Pollsquestion(Base):
    __tablename__ = 'pollsquestion'
    __table_args__ = (
        Index('ix_f910bbb4', 'uuid_', 'companyid'),
        Index('ix_f3c9f36', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    questionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    title = Column(Text)
    description = Column(Text)
    expirationdate = Column(DateTime)
    lastvotedate = Column(DateTime)


class Pollsvote(Base):
    __tablename__ = 'pollsvote'
    __table_args__ = (
        Index('ix_1bbfd4d3', 'questionid', 'userid', unique=True),
        Index('ix_7d8e92b8', 'uuid_', 'companyid'),
        Index('ix_a88c673a', 'uuid_', 'groupid', unique=True)
    )

    voteid = Column(BigInteger, primary_key=True)
    userid = Column(BigInteger)
    questionid = Column(BigInteger, index=True)
    choiceid = Column(BigInteger, index=True)
    votedate = Column(DateTime)
    companyid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    uuid_ = Column(String(75), index=True)
    groupid = Column(BigInteger)


class Portalpreference(Base):
    __tablename__ = 'portalpreferences'
    __table_args__ = (
        Index('ix_d1f795f1', 'ownerid', 'ownertype'),
    )

    portalpreferencesid = Column(BigInteger, primary_key=True)
    ownerid = Column(BigInteger)
    ownertype = Column(Integer)
    preferences = Column(Text)


class Portlet(Base):
    __tablename__ = 'portlet'
    __table_args__ = (
        Index('ix_12b5e51d', 'companyid', 'portletid', unique=True),
    )

    id_ = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    portletid = Column(String(200))
    roles = Column(Text)
    active_ = Column(Boolean)


class Portletitem(Base):
    __tablename__ = 'portletitem'
    __table_args__ = (
        Index('ix_d699243f', 'groupid', 'name', 'portletid', 'classnameid'),
        Index('ix_96bdd537', 'groupid', 'classnameid'),
        Index('ix_2c61314e', 'groupid', 'portletid'),
        Index('ix_e922d6c0', 'groupid', 'portletid', 'classnameid'),
        Index('ix_33b8ce8d', 'groupid', 'portletid', 'name'),
        Index('ix_8e71167f', 'groupid', 'portletid', 'classnameid', 'name')
    )

    portletitemid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    portletid = Column(String(200))
    classnameid = Column(BigInteger)


class Portletpreference(Base):
    __tablename__ = 'portletpreferences'
    __table_args__ = (
        Index('ix_d5eda3a1', 'ownertype', 'plid', 'portletid'),
        Index('ix_c9a3fce2', 'ownerid', 'ownertype', 'portletid'),
        Index('ix_a3b2a80c', 'ownertype', 'portletid'),
        Index('ix_e4f13e6e', 'ownerid', 'ownertype', 'plid'),
        Index('ix_c7057ff7', 'ownerid', 'ownertype', 'plid', 'portletid', unique=True),
        Index('ix_d340db76', 'plid', 'portletid')
    )

    portletpreferencesid = Column(BigInteger, primary_key=True)
    ownerid = Column(BigInteger)
    ownertype = Column(Integer)
    plid = Column(BigInteger, index=True)
    portletid = Column(String(200), index=True)
    preferences = Column(Text)


class QuartzBlobTrigger(Base):
    __tablename__ = 'quartz_blob_triggers'

    sched_name = Column(String(120), primary_key=True, nullable=False)
    trigger_name = Column(String(200), primary_key=True, nullable=False)
    trigger_group = Column(String(200), primary_key=True, nullable=False)
    blob_data = Column(LargeBinary)


class QuartzCalendar(Base):
    __tablename__ = 'quartz_calendars'

    sched_name = Column(String(120), primary_key=True, nullable=False)
    calendar_name = Column(String(200), primary_key=True, nullable=False)
    calendar = Column(LargeBinary, nullable=False)


class QuartzCronTrigger(Base):
    __tablename__ = 'quartz_cron_triggers'

    sched_name = Column(String(120), primary_key=True, nullable=False)
    trigger_name = Column(String(200), primary_key=True, nullable=False)
    trigger_group = Column(String(200), primary_key=True, nullable=False)
    cron_expression = Column(String(200), nullable=False)
    time_zone_id = Column(String(80))


class QuartzFiredTrigger(Base):
    __tablename__ = 'quartz_fired_triggers'
    __table_args__ = (
        Index('ix_bc2f03b0', 'sched_name', 'job_group'),
        Index('ix_4bd722bm', 'sched_name', 'trigger_group'),
        Index('ix_be3835e5', 'sched_name', 'trigger_name', 'trigger_group'),
        Index('ix_5005e3af', 'sched_name', 'job_name', 'job_group'),
        Index('ix_204d31e8', 'sched_name', 'instance_name'),
        Index('ix_339e078m', 'sched_name', 'instance_name', 'requests_recovery')
    )

    sched_name = Column(String(120), primary_key=True, nullable=False)
    entry_id = Column(String(95), primary_key=True, nullable=False)
    trigger_name = Column(String(200), nullable=False)
    trigger_group = Column(String(200), nullable=False)
    instance_name = Column(String(200), nullable=False)
    fired_time = Column(BigInteger, nullable=False)
    priority = Column(Integer, nullable=False)
    state = Column(String(16), nullable=False)
    job_name = Column(String(200))
    job_group = Column(String(200))
    is_nonconcurrent = Column(Boolean)
    requests_recovery = Column(Boolean)


class QuartzJobDetail(Base):
    __tablename__ = 'quartz_job_details'
    __table_args__ = (
        Index('ix_88328984', 'sched_name', 'job_group'),
        Index('ix_779bca37', 'sched_name', 'requests_recovery')
    )

    sched_name = Column(String(120), primary_key=True, nullable=False)
    job_name = Column(String(200), primary_key=True, nullable=False)
    job_group = Column(String(200), primary_key=True, nullable=False)
    description = Column(String(250))
    job_class_name = Column(String(250), nullable=False)
    is_durable = Column(Boolean, nullable=False)
    is_nonconcurrent = Column(Boolean, nullable=False)
    is_update_data = Column(Boolean, nullable=False)
    requests_recovery = Column(Boolean, nullable=False)
    job_data = Column(LargeBinary)


class QuartzLock(Base):
    __tablename__ = 'quartz_locks'

    sched_name = Column(String(120), primary_key=True, nullable=False)
    lock_name = Column(String(40), primary_key=True, nullable=False)


class QuartzPausedTriggerGrp(Base):
    __tablename__ = 'quartz_paused_trigger_grps'

    sched_name = Column(String(120), primary_key=True, nullable=False)
    trigger_group = Column(String(200), primary_key=True, nullable=False)


class QuartzSchedulerState(Base):
    __tablename__ = 'quartz_scheduler_state'

    sched_name = Column(String(120), primary_key=True, nullable=False)
    instance_name = Column(String(200), primary_key=True, nullable=False)
    last_checkin_time = Column(BigInteger, nullable=False)
    checkin_interval = Column(BigInteger, nullable=False)


class QuartzSimpleTrigger(Base):
    __tablename__ = 'quartz_simple_triggers'

    sched_name = Column(String(120), primary_key=True, nullable=False)
    trigger_name = Column(String(200), primary_key=True, nullable=False)
    trigger_group = Column(String(200), primary_key=True, nullable=False)
    repeat_count = Column(BigInteger, nullable=False)
    repeat_interval = Column(BigInteger, nullable=False)
    times_triggered = Column(BigInteger, nullable=False)


class QuartzSimpropTrigger(Base):
    __tablename__ = 'quartz_simprop_triggers'

    sched_name = Column(String(120), primary_key=True, nullable=False)
    trigger_name = Column(String(200), primary_key=True, nullable=False)
    trigger_group = Column(String(200), primary_key=True, nullable=False)
    str_prop_1 = Column(String(512))
    str_prop_2 = Column(String(512))
    str_prop_3 = Column(String(512))
    int_prop_1 = Column(Integer)
    int_prop_2 = Column(Integer)
    long_prop_1 = Column(BigInteger)
    long_prop_2 = Column(BigInteger)
    dec_prop_1 = Column(Numeric(13, 4))
    dec_prop_2 = Column(Numeric(13, 4))
    bool_prop_1 = Column(Boolean)
    bool_prop_2 = Column(Boolean)


class QuartzTrigger(Base):
    __tablename__ = 'quartz_triggers'
    __table_args__ = (
        Index('ix_d219afde', 'sched_name', 'trigger_group', 'trigger_state'),
        Index('ix_1f92813c', 'sched_name', 'next_fire_time', 'misfire_instr'),
        Index('ix_186442a4', 'sched_name', 'trigger_name', 'trigger_group', 'trigger_state'),
        Index('ix_eefe382a', 'sched_name', 'next_fire_time'),
        Index('ix_1ba1f9dc', 'sched_name', 'trigger_group'),
        Index('ix_f026cf4c', 'sched_name', 'next_fire_time', 'trigger_state'),
        Index('ix_cd7132d0', 'sched_name', 'calendar_name'),
        Index('ix_8aa50be1', 'sched_name', 'job_group'),
        Index('ix_f2dd7c7e', 'sched_name', 'next_fire_time', 'trigger_state', 'misfire_instr'),
        Index('ix_99108b6e', 'sched_name', 'trigger_state'),
        Index('ix_91ca7cce', 'sched_name', 'trigger_group', 'next_fire_time', 'trigger_state', 'misfire_instr'),
        Index('ix_a85822a0', 'sched_name', 'job_name', 'job_group')
    )

    sched_name = Column(String(120), primary_key=True, nullable=False)
    trigger_name = Column(String(200), primary_key=True, nullable=False)
    trigger_group = Column(String(200), primary_key=True, nullable=False)
    job_name = Column(String(200), nullable=False)
    job_group = Column(String(200), nullable=False)
    description = Column(String(250))
    next_fire_time = Column(BigInteger)
    prev_fire_time = Column(BigInteger)
    priority = Column(Integer)
    trigger_state = Column(String(16), nullable=False)
    trigger_type = Column(String(8), nullable=False)
    start_time = Column(BigInteger, nullable=False)
    end_time = Column(BigInteger)
    calendar_name = Column(String(200))
    misfire_instr = Column(Integer)
    job_data = Column(LargeBinary)


class Ratingsentry(Base):
    __tablename__ = 'ratingsentry'
    __table_args__ = (
        Index('ix_16184d57', 'classnameid', 'classpk'),
        Index('ix_b47e3c11', 'userid', 'classnameid', 'classpk', unique=True),
        Index('ix_a1a8cb8b', 'classnameid', 'classpk', 'score')
    )

    entryid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    score = Column(Float(53))


class Ratingsstat(Base):
    __tablename__ = 'ratingsstats'
    __table_args__ = (
        Index('ix_a6e99284', 'classnameid', 'classpk', unique=True),
    )

    statsid = Column(BigInteger, primary_key=True)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    totalentries = Column(Integer)
    totalscore = Column(Float(53))
    averagescore = Column(Float(53))


class Region(Base):
    __tablename__ = 'region'
    __table_args__ = (
        Index('ix_11fb3e42', 'countryid', 'active_'),
        Index('ix_a2635f5c', 'countryid', 'regioncode', unique=True)
    )

    regionid = Column(BigInteger, primary_key=True)
    countryid = Column(BigInteger, index=True)
    regioncode = Column(String(75))
    name = Column(String(75))
    active_ = Column(Boolean, index=True)


class Release(Base):
    __tablename__ = 'release_'

    releaseid = Column(BigInteger, primary_key=True)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    servletcontextname = Column(String(75), index=True)
    buildnumber = Column(Integer)
    builddate = Column(DateTime)
    verified = Column(Boolean)
    teststring = Column(String(1024))
    state_ = Column(Integer)


class Repository(Base):
    __tablename__ = 'repository'
    __table_args__ = (
        Index('ix_60c8634c', 'groupid', 'name', 'portletid', unique=True),
        Index('ix_11641e26', 'uuid_', 'groupid', unique=True),
        Index('ix_f543ea4', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    repositoryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    name = Column(String(75))
    description = Column(Text)
    portletid = Column(String(200))
    typesettings = Column(Text)
    dlfolderid = Column(BigInteger)


class Repositoryentry(Base):
    __tablename__ = 'repositoryentry'
    __table_args__ = (
        Index('ix_d3b9af62', 'uuid_', 'companyid'),
        Index('ix_9bdcf489', 'repositoryid', 'mappedid', unique=True),
        Index('ix_354aa664', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    repositoryentryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    repositoryid = Column(BigInteger, index=True)
    mappedid = Column(String(75))
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    manualcheckinrequired = Column(Boolean)


class Resourceaction(Base):
    __tablename__ = 'resourceaction'
    __table_args__ = (
        Index('ix_edb9986e', 'name', 'actionid', unique=True),
    )

    resourceactionid = Column(BigInteger, primary_key=True)
    name = Column(String(255), index=True)
    actionid = Column(String(75))
    bitwisevalue = Column(BigInteger)


class Resourceblock(Base):
    __tablename__ = 'resourceblock'
    __table_args__ = (
        Index('ix_da30b086', 'companyid', 'groupid', 'name'),
        Index('ix_2d4cc782', 'companyid', 'name'),
        Index('ix_aeea209c', 'companyid', 'groupid', 'name', 'permissionshash', unique=True)
    )

    resourceblockid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    groupid = Column(BigInteger)
    name = Column(String(75))
    permissionshash = Column(String(75))
    referencecount = Column(BigInteger)


class Resourceblockpermission(Base):
    __tablename__ = 'resourceblockpermission'
    __table_args__ = (
        Index('ix_d63d20bb', 'resourceblockid', 'roleid', unique=True),
    )

    resourceblockpermissionid = Column(BigInteger, primary_key=True)
    resourceblockid = Column(BigInteger, index=True)
    roleid = Column(BigInteger, index=True)
    actionids = Column(BigInteger)


class Resourcepermission(Base):
    __tablename__ = 'resourcepermission'
    __table_args__ = (
        Index('ix_26284944', 'companyid', 'primkey'),
        Index('ix_8d83d0ce', 'companyid', 'name', 'scope', 'primkey', 'roleid', unique=True),
        Index('ix_2f80c17c', 'roleid', 'scope'),
        Index('ix_d2e2b644', 'companyid', 'name', 'scope', 'primkey', 'roleid', 'actionids'),
        Index('ix_60b99860', 'companyid', 'name', 'scope'),
        Index('ix_2200aa69', 'companyid', 'name', 'scope', 'primkey')
    )

    resourcepermissionid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    name = Column(String(255))
    scope = Column(Integer, index=True)
    primkey = Column(String(255))
    roleid = Column(BigInteger, index=True)
    actionids = Column(BigInteger)
    ownerid = Column(BigInteger)


class Resourcetypepermission(Base):
    __tablename__ = 'resourcetypepermission'
    __table_args__ = (
        Index('ix_ba497163', 'companyid', 'groupid', 'name', 'roleid', unique=True),
        Index('ix_7d81f66f', 'companyid', 'name', 'roleid')
    )

    resourcetypepermissionid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    groupid = Column(BigInteger)
    name = Column(String(75))
    roleid = Column(BigInteger, index=True)
    actionids = Column(BigInteger)


class Role(Base):
    __tablename__ = 'role_'
    __table_args__ = (
        Index('ix_a88e424e', 'companyid', 'classnameid', 'classpk', unique=True),
        Index('ix_ebc931b8', 'companyid', 'name', unique=True),
        Index('ix_f3e1c6fc', 'companyid', 'type_'),
        Index('ix_b9ff6043', 'uuid_', 'companyid'),
        Index('ix_cbe204', 'type_', 'subtype')
    )

    roleid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    name = Column(String(75), index=True)
    title = Column(Text)
    description = Column(Text)
    type_ = Column(Integer, index=True)
    subtype = Column(String(75), index=True)
    uuid_ = Column(String(75), index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)


class ScframeworkversiScproductver(Base):
    __tablename__ = 'scframeworkversi_scproductvers'

    frameworkversionid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    productversionid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class Scframeworkversion(Base):
    __tablename__ = 'scframeworkversion'
    __table_args__ = (
        Index('ix_6e1764f', 'groupid', 'active_'),
    )

    frameworkversionid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    url = Column(Text)
    active_ = Column(Boolean)
    priority = Column(Integer)


class Sclicense(Base):
    __tablename__ = 'sclicense'
    __table_args__ = (
        Index('ix_5327bb79', 'active_', 'recommended'),
    )

    licenseid = Column(BigInteger, primary_key=True)
    name = Column(String(75))
    url = Column(Text)
    opensource = Column(Boolean)
    active_ = Column(Boolean, index=True)
    recommended = Column(Boolean)


class SclicensesScproductentry(Base):
    __tablename__ = 'sclicenses_scproductentries'

    licenseid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    productentryid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class Scproductentry(Base):
    __tablename__ = 'scproductentry'
    __table_args__ = (
        Index('ix_98e6a9cb', 'groupid', 'userid'),
        Index('ix_7311e812', 'repogroupid', 'repoartifactid')
    )

    productentryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    type_ = Column(String(75))
    tags = Column(String(255))
    shortdescription = Column(Text)
    longdescription = Column(Text)
    pageurl = Column(Text)
    author = Column(String(75))
    repogroupid = Column(String(75))
    repoartifactid = Column(String(75))


class Scproductscreenshot(Base):
    __tablename__ = 'scproductscreenshot'
    __table_args__ = (
        Index('ix_da913a55', 'productentryid', 'priority'),
    )

    productscreenshotid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    groupid = Column(BigInteger)
    productentryid = Column(BigInteger, index=True)
    thumbnailid = Column(BigInteger, index=True)
    fullimageid = Column(BigInteger, index=True)
    priority = Column(Integer)


class Scproductversion(Base):
    __tablename__ = 'scproductversion'

    productversionid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    productentryid = Column(BigInteger, index=True)
    version = Column(String(75))
    changelog = Column(Text)
    downloadpageurl = Column(Text)
    directdownloadurl = Column(String(2000), index=True)
    repostoreartifact = Column(Boolean)


class Servicecomponent(Base):
    __tablename__ = 'servicecomponent'
    __table_args__ = (
        Index('ix_4f0315b8', 'buildnamespace', 'buildnumber', unique=True),
    )

    servicecomponentid = Column(BigInteger, primary_key=True)
    buildnamespace = Column(String(75), index=True)
    buildnumber = Column(BigInteger)
    builddate = Column(BigInteger)
    data_ = Column(Text)


class Shard(Base):
    __tablename__ = 'shard'
    __table_args__ = (
        Index('ix_da5f4359', 'classnameid', 'classpk'),
    )

    shardid = Column(BigInteger, primary_key=True)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    name = Column(String(75), index=True)


class Shoppingcart(Base):
    __tablename__ = 'shoppingcart'
    __table_args__ = (
        Index('ix_fc46fe16', 'groupid', 'userid', unique=True),
    )

    cartid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    itemids = Column(Text)
    couponcodes = Column(String(75))
    altshipping = Column(Integer)
    insure = Column(Boolean)


class Shoppingcategory(Base):
    __tablename__ = 'shoppingcategory'
    __table_args__ = (
        Index('ix_1e6464f5', 'groupid', 'parentcategoryid'),
    )

    categoryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    parentcategoryid = Column(BigInteger)
    name = Column(String(75))
    description = Column(Text)


class Shoppingcoupon(Base):
    __tablename__ = 'shoppingcoupon'

    couponid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    code_ = Column(String(75), unique=True)
    name = Column(String(75))
    description = Column(Text)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    active_ = Column(Boolean)
    limitcategories = Column(Text)
    limitskus = Column(Text)
    minorder = Column(Float(53))
    discount = Column(Float(53))
    discounttype = Column(String(75))


class Shoppingitem(Base):
    __tablename__ = 'shoppingitem'
    __table_args__ = (
        Index('ix_fefe7d76', 'groupid', 'categoryid'),
        Index('ix_1c717ca6', 'companyid', 'sku', unique=True)
    )

    itemid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    categoryid = Column(BigInteger)
    sku = Column(String(75))
    name = Column(String(200))
    description = Column(Text)
    properties = Column(Text)
    fields_ = Column(Boolean)
    fieldsquantities = Column(Text)
    minquantity = Column(Integer)
    maxquantity = Column(Integer)
    price = Column(Float(53))
    discount = Column(Float(53))
    taxable = Column(Boolean)
    shipping = Column(Float(53))
    useshippingformula = Column(Boolean)
    requiresshipping = Column(Boolean)
    stockquantity = Column(Integer)
    featured_ = Column(Boolean)
    sale_ = Column(Boolean)
    smallimage = Column(Boolean)
    smallimageid = Column(BigInteger, index=True)
    smallimageurl = Column(Text)
    mediumimage = Column(Boolean)
    mediumimageid = Column(BigInteger, index=True)
    mediumimageurl = Column(Text)
    largeimage = Column(Boolean)
    largeimageid = Column(BigInteger, index=True)
    largeimageurl = Column(Text)


class Shoppingitemfield(Base):
    __tablename__ = 'shoppingitemfield'

    itemfieldid = Column(BigInteger, primary_key=True)
    itemid = Column(BigInteger, index=True)
    name = Column(String(75))
    values_ = Column(Text)
    description = Column(Text)


class Shoppingitemprice(Base):
    __tablename__ = 'shoppingitemprice'

    itempriceid = Column(BigInteger, primary_key=True)
    itemid = Column(BigInteger, index=True)
    minquantity = Column(Integer)
    maxquantity = Column(Integer)
    price = Column(Float(53))
    discount = Column(Float(53))
    taxable = Column(Boolean)
    shipping = Column(Float(53))
    useshippingformula = Column(Boolean)
    status = Column(Integer)


class Shoppingorder(Base):
    __tablename__ = 'shoppingorder'
    __table_args__ = (
        Index('ix_119b5630', 'groupid', 'userid', 'pppaymentstatus'),
    )

    orderid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    number_ = Column(String(75), unique=True)
    tax = Column(Float(53))
    shipping = Column(Float(53))
    altshipping = Column(String(75))
    requiresshipping = Column(Boolean)
    insure = Column(Boolean)
    insurance = Column(Float(53))
    couponcodes = Column(String(75))
    coupondiscount = Column(Float(53))
    billingfirstname = Column(String(75))
    billinglastname = Column(String(75))
    billingemailaddress = Column(String(75))
    billingcompany = Column(String(75))
    billingstreet = Column(String(75))
    billingcity = Column(String(75))
    billingstate = Column(String(75))
    billingzip = Column(String(75))
    billingcountry = Column(String(75))
    billingphone = Column(String(75))
    shiptobilling = Column(Boolean)
    shippingfirstname = Column(String(75))
    shippinglastname = Column(String(75))
    shippingemailaddress = Column(String(75))
    shippingcompany = Column(String(75))
    shippingstreet = Column(String(75))
    shippingcity = Column(String(75))
    shippingstate = Column(String(75))
    shippingzip = Column(String(75))
    shippingcountry = Column(String(75))
    shippingphone = Column(String(75))
    ccname = Column(String(75))
    cctype = Column(String(75))
    ccnumber = Column(String(75))
    ccexpmonth = Column(Integer)
    ccexpyear = Column(Integer)
    ccvernumber = Column(String(75))
    comments = Column(Text)
    pptxnid = Column(String(75), index=True)
    pppaymentstatus = Column(String(75))
    pppaymentgross = Column(Float(53))
    ppreceiveremail = Column(String(75))
    pppayeremail = Column(String(75))
    sendorderemail = Column(Boolean)
    sendshippingemail = Column(Boolean)


class Shoppingorderitem(Base):
    __tablename__ = 'shoppingorderitem'

    orderitemid = Column(BigInteger, primary_key=True)
    orderid = Column(BigInteger, index=True)
    itemid = Column(String(75))
    sku = Column(String(75))
    name = Column(String(200))
    description = Column(Text)
    properties = Column(Text)
    price = Column(Float(53))
    quantity = Column(Integer)
    shippeddate = Column(DateTime)


class SnMeetupsentry(Base):
    __tablename__ = 'sn_meetupsentry'

    meetupsentryid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    title = Column(String(75))
    description = Column(Text)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    totalattendees = Column(Integer)
    maxattendees = Column(Integer)
    price = Column(Float(53))
    thumbnailid = Column(BigInteger)


class SnMeetupsregistration(Base):
    __tablename__ = 'sn_meetupsregistration'
    __table_args__ = (
        Index('ix_3cbe4c36', 'userid', 'meetupsentryid'),
        Index('ix_bceb16e2', 'meetupsentryid', 'status')
    )

    meetupsregistrationid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    meetupsentryid = Column(BigInteger, index=True)
    status = Column(Integer)
    comments = Column(Text)


class SnWallentry(Base):
    __tablename__ = 'sn_wallentry'
    __table_args__ = (
        Index('ix_f2f6c19a', 'groupid', 'userid'),
    )

    wallentryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    comments = Column(Text)


class Socialactivity(Base):
    __tablename__ = 'socialactivity'
    __table_args__ = (
        Index('ix_8f32dec9', 'groupid', 'userid', 'createdate', 'classnameid', 'classpk', 'type_', 'receiveruserid', unique=True),
        Index('ix_fb604dc7', 'groupid', 'userid', 'classnameid', 'classpk', 'type_', 'receiveruserid'),
        Index('ix_d0e9029e', 'classnameid', 'classpk', 'type_'),
        Index('ix_a853c757', 'classnameid', 'classpk'),
        Index('ix_1f00c374', 'mirroractivityid', 'classnameid', 'classpk')
    )

    activityid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    createdate = Column(BigInteger)
    mirroractivityid = Column(BigInteger, index=True)
    classnameid = Column(BigInteger, index=True)
    classpk = Column(BigInteger)
    type_ = Column(Integer)
    extradata = Column(Text)
    receiveruserid = Column(BigInteger, index=True)
    activitysetid = Column(BigInteger, index=True)
    parentclassnameid = Column(BigInteger)
    parentclasspk = Column(BigInteger)


class Socialactivityachievement(Base):
    __tablename__ = 'socialactivityachievement'
    __table_args__ = (
        Index('ix_c8fd892b', 'groupid', 'userid'),
        Index('ix_8f6408f0', 'groupid', 'name'),
        Index('ix_83e16f2f', 'groupid', 'firstingroup'),
        Index('ix_d4390caa', 'groupid', 'userid', 'name', unique=True),
        Index('ix_aabc18e9', 'groupid', 'userid', 'firstingroup')
    )

    activityachievementid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    createdate = Column(BigInteger)
    name = Column(String(75))
    firstingroup = Column(Boolean)


class Socialactivitycounter(Base):
    __tablename__ = 'socialactivitycounter'
    __table_args__ = (
        Index('ix_926cdd04', 'groupid', 'classnameid', 'classpk', 'ownertype'),
        Index('ix_a4b9a23b', 'classnameid', 'classpk'),
        Index('ix_374b35ae', 'groupid', 'classnameid', 'classpk', 'name', 'ownertype', 'startperiod', unique=True),
        Index('ix_1b7e3b67', 'groupid', 'classnameid', 'classpk', 'name', 'ownertype', 'endperiod', unique=True)
    )

    activitycounterid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    name = Column(String(75))
    ownertype = Column(Integer)
    currentvalue = Column(Integer)
    totalvalue = Column(Integer)
    gracevalue = Column(Integer)
    startperiod = Column(Integer)
    endperiod = Column(Integer)
    active_ = Column(Boolean)


class Socialactivitylimit(Base):
    __tablename__ = 'socialactivitylimit'
    __table_args__ = (
        Index('ix_f1c1a617', 'groupid', 'userid', 'classnameid', 'classpk', 'activitytype', 'activitycountername', unique=True),
        Index('ix_b15863fa', 'classnameid', 'classpk')
    )

    activitylimitid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    activitytype = Column(Integer)
    activitycountername = Column(String(75))
    value = Column(String(75))


class Socialactivityset(Base):
    __tablename__ = 'socialactivityset'
    __table_args__ = (
        Index('ix_62ac101a', 'userid', 'classnameid', 'classpk', 'type_'),
        Index('ix_9be30ddf', 'groupid', 'userid', 'classnameid', 'type_'),
        Index('ix_f71071bd', 'groupid', 'userid', 'type_'),
        Index('ix_4460fa14', 'classnameid', 'classpk', 'type_')
    )

    activitysetid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    createdate = Column(BigInteger)
    modifieddate = Column(BigInteger)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    type_ = Column(Integer)
    extradata = Column(Text)
    activitycount = Column(Integer)


class Socialactivitysetting(Base):
    __tablename__ = 'socialactivitysetting'
    __table_args__ = (
        Index('ix_9d22151e', 'groupid', 'classnameid'),
        Index('ix_384788cd', 'groupid', 'activitytype'),
        Index('ix_d984aaba', 'groupid', 'classnameid', 'activitytype', 'name'),
        Index('ix_1e9cf33b', 'groupid', 'classnameid', 'activitytype')
    )

    activitysettingid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    classnameid = Column(BigInteger)
    activitytype = Column(Integer)
    name = Column(String(75))
    value = Column(String(1024))


class Socialrelation(Base):
    __tablename__ = 'socialrelation'
    __table_args__ = (
        Index('ix_12a92145', 'userid1', 'userid2', 'type_', unique=True),
        Index('ix_4b52be89', 'userid1', 'type_'),
        Index('ix_3f9c2fa8', 'userid2', 'type_'),
        Index('ix_b5c9c690', 'userid1', 'userid2'),
        Index('ix_5b30f663', 'uuid_', 'companyid'),
        Index('ix_95135d1c', 'companyid', 'type_')
    )

    uuid_ = Column(String(75), index=True)
    relationid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    createdate = Column(BigInteger)
    userid1 = Column(BigInteger, index=True)
    userid2 = Column(BigInteger, index=True)
    type_ = Column(Integer, index=True)


class Socialrequest(Base):
    __tablename__ = 'socialrequest'
    __table_args__ = (
        Index('ix_d9380cb7', 'receiveruserid', 'status'),
        Index('ix_36a90ca7', 'userid', 'classnameid', 'classpk', 'type_', 'receiveruserid', unique=True),
        Index('ix_d3425487', 'classnameid', 'classpk', 'type_', 'receiveruserid', 'status'),
        Index('ix_cc86a444', 'userid', 'classnameid', 'classpk', 'type_', 'status'),
        Index('ix_4f973efe', 'uuid_', 'groupid', unique=True),
        Index('ix_ab5906a8', 'userid', 'status'),
        Index('ix_8d42897c', 'uuid_', 'companyid')
    )

    uuid_ = Column(String(75), index=True)
    requestid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    createdate = Column(BigInteger)
    modifieddate = Column(BigInteger)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    type_ = Column(Integer)
    extradata = Column(Text)
    receiveruserid = Column(BigInteger, index=True)
    status = Column(Integer)


class SpatialRefSy(Base):
    __tablename__ = 'spatial_ref_sys'

    srid = Column(Integer, primary_key=True)
    auth_name = Column(String(256))
    auth_srid = Column(Integer)
    srtext = Column(String(2048))
    proj4text = Column(String(2048))


class Subscription(Base):
    __tablename__ = 'subscription'
    __table_args__ = (
        Index('ix_2e1a92d4', 'companyid', 'userid', 'classnameid', 'classpk', unique=True),
        Index('ix_e8f34171', 'userid', 'classnameid'),
        Index('ix_786d171a', 'companyid', 'classnameid', 'classpk')
    )

    subscriptionid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    frequency = Column(String(75))


class Syncdlobject(Base):
    __tablename__ = 'syncdlobject'
    __table_args__ = (
        Index('ix_7f996123', 'companyid', 'modifiedtime', 'repositoryid'),
    )

    objectid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    createtime = Column(BigInteger)
    modifiedtime = Column(BigInteger)
    repositoryid = Column(BigInteger)
    parentfolderid = Column(BigInteger)
    name = Column(String(255))
    extension = Column(String(75))
    mimetype = Column(String(75))
    description = Column(Text)
    changelog = Column(String(75))
    extrasettings = Column(Text)
    version = Column(String(75))
    size_ = Column(BigInteger)
    checksum = Column(String(75))
    event = Column(String(75))
    lockexpirationdate = Column(DateTime)
    lockuserid = Column(BigInteger)
    lockusername = Column(String(75))
    type_ = Column(String(75))
    typepk = Column(BigInteger, unique=True)
    typeuuid = Column(String(75))


class Systemevent(Base):
    __tablename__ = 'systemevent'
    __table_args__ = (
        Index('ix_7a2f0ece', 'groupid', 'classnameid', 'classpk'),
        Index('ix_ffcbb747', 'groupid', 'classnameid', 'classpk', 'type_'),
        Index('ix_a19c89ff', 'groupid', 'systemeventsetkey')
    )

    systemeventid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    classuuid = Column(String(75))
    referrerclassnameid = Column(BigInteger)
    parentsystemeventid = Column(BigInteger)
    systemeventsetkey = Column(BigInteger)
    type_ = Column(Integer)
    extradata = Column(Text)


class Tasksproposal(Base):
    __tablename__ = 'tasksproposal'
    __table_args__ = (
        Index('ix_181a4a1b', 'classnameid', 'classpk', unique=True),
        Index('ix_6eec675e', 'groupid', 'userid')
    )

    proposalid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(String(75))
    name = Column(String(75))
    description = Column(Text)
    publishdate = Column(DateTime)
    duedate = Column(DateTime)


class Tasksreview(Base):
    __tablename__ = 'tasksreview'
    __table_args__ = (
        Index('ix_5c6be4c7', 'userid', 'proposalid', unique=True),
        Index('ix_1894b29a', 'proposalid', 'stage', 'completed'),
        Index('ix_70afea01', 'proposalid', 'stage'),
        Index('ix_41afc20c', 'proposalid', 'stage', 'completed', 'rejected')
    )

    reviewid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    proposalid = Column(BigInteger, index=True)
    assignedbyuserid = Column(BigInteger)
    assignedbyusername = Column(String(75))
    stage = Column(Integer)
    completed = Column(Boolean)
    rejected = Column(Boolean)


class Team(Base):
    __tablename__ = 'team'
    __table_args__ = (
        Index('ix_143dc786', 'groupid', 'name', unique=True),
    )

    teamid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    groupid = Column(BigInteger, index=True)
    name = Column(String(75))
    description = Column(Text)


class Ticket(Base):
    __tablename__ = 'ticket'

    ticketid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    createdate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    key_ = Column(String(75), index=True)
    expirationdate = Column(DateTime)
    type_ = Column(Integer)
    extrainfo = Column(Text)


class Trashentry(Base):
    __tablename__ = 'trashentry'
    __table_args__ = (
        Index('ix_b35f73d5', 'classnameid', 'classpk', unique=True),
        Index('ix_6caae2e8', 'groupid', 'createdate'),
        Index('ix_fc4eea64', 'groupid', 'classnameid')
    )

    entryid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    systemeventsetkey = Column(BigInteger)
    typesettings = Column(Text)
    status = Column(Integer)


class Trashversion(Base):
    __tablename__ = 'trashversion'
    __table_args__ = (
        Index('ix_d639348c', 'entryid', 'classnameid', 'classpk', unique=True),
        Index('ix_72d58d37', 'entryid', 'classnameid'),
        Index('ix_630a643b', 'classnameid', 'classpk')
    )

    versionid = Column(BigInteger, primary_key=True)
    entryid = Column(BigInteger, index=True)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    typesettings = Column(Text)
    status = Column(Integer)


class User(Base):
    __tablename__ = 'user_'
    __table_args__ = (
        Index('ix_615e9f7a', 'companyid', 'emailaddress', unique=True),
        Index('ix_c5806019', 'companyid', 'screenname', unique=True),
        Index('ix_6ef03e4e', 'companyid', 'defaultuser'),
        Index('ix_740c4d0c', 'companyid', 'createdate'),
        Index('ix_1d731f03', 'companyid', 'facebookid'),
        Index('ix_9782ad88', 'companyid', 'userid', unique=True),
        Index('ix_ee8abd19', 'companyid', 'modifieddate'),
        Index('ix_89509087', 'companyid', 'openid'),
        Index('ix_bcfda257', 'companyid', 'createdate', 'modifieddate'),
        Index('ix_405cc0e', 'uuid_', 'companyid'),
        Index('ix_f6039434', 'companyid', 'status')
    )

    uuid_ = Column(String(75), index=True)
    userid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    defaultuser = Column(Boolean)
    contactid = Column(BigInteger, unique=True)
    password_ = Column(String(75))
    passwordencrypted = Column(Boolean)
    passwordreset = Column(Boolean)
    passwordmodifieddate = Column(DateTime)
    digest = Column(String(255))
    reminderqueryquestion = Column(String(75))
    reminderqueryanswer = Column(String(75))
    gracelogincount = Column(Integer)
    screenname = Column(String(75))
    emailaddress = Column(String(75), index=True)
    facebookid = Column(BigInteger)
    openid = Column(String(1024))
    portraitid = Column(BigInteger, index=True)
    languageid = Column(String(75))
    timezoneid = Column(String(75))
    greeting = Column(String(255))
    comments = Column(Text)
    firstname = Column(String(75))
    middlename = Column(String(75))
    lastname = Column(String(75))
    jobtitle = Column(String(100))
    logindate = Column(DateTime)
    loginip = Column(String(75))
    lastlogindate = Column(DateTime)
    lastloginip = Column(String(75))
    lastfailedlogindate = Column(DateTime)
    failedloginattempts = Column(Integer)
    lockout = Column(Boolean)
    lockoutdate = Column(DateTime)
    agreedtotermsofuse = Column(Boolean)
    emailaddressverified = Column(Boolean)
    status = Column(Integer)
    ldapserverid = Column(BigInteger)


class Usergroup(Base):
    __tablename__ = 'usergroup'
    __table_args__ = (
        Index('ix_72394f8e', 'uuid_', 'companyid'),
        Index('ix_23ead0d', 'companyid', 'name', unique=True),
        Index('ix_69771487', 'companyid', 'parentusergroupid')
    )

    usergroupid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    parentusergroupid = Column(BigInteger)
    name = Column(String(75))
    description = Column(Text)
    addedbyldapimport = Column(Boolean)
    uuid_ = Column(String(75), index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)


class Usergroupgrouprole(Base):
    __tablename__ = 'usergroupgrouprole'
    __table_args__ = (
        Index('ix_cab0ccc8', 'groupid', 'roleid'),
        Index('ix_73c52252', 'usergroupid', 'groupid')
    )

    usergroupid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    groupid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    roleid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class Usergrouprole(Base):
    __tablename__ = 'usergrouprole'
    __table_args__ = (
        Index('ix_871412df', 'groupid', 'roleid'),
        Index('ix_4d040680', 'userid', 'groupid')
    )

    userid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    groupid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    roleid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class UsergroupsTeam(Base):
    __tablename__ = 'usergroups_teams'

    usergroupid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    teamid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class Useridmapper(Base):
    __tablename__ = 'useridmapper'
    __table_args__ = (
        Index('ix_41a32e0d', 'type_', 'externaluserid', unique=True),
        Index('ix_d1c44a6e', 'userid', 'type_', unique=True)
    )

    useridmapperid = Column(BigInteger, primary_key=True)
    userid = Column(BigInteger, index=True)
    type_ = Column(String(75))
    description = Column(String(75))
    externaluserid = Column(String(75))


class Usernotificationdelivery(Base):
    __tablename__ = 'usernotificationdelivery'
    __table_args__ = (
        Index('ix_8b6e3ace', 'userid', 'portletid', 'classnameid', 'notificationtype', 'deliverytype', unique=True),
    )

    usernotificationdeliveryid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    portletid = Column(String(200))
    classnameid = Column(BigInteger)
    notificationtype = Column(Integer)
    deliverytype = Column(Integer)
    deliver = Column(Boolean)


class Usernotificationevent(Base):
    __tablename__ = 'usernotificationevent'
    __table_args__ = (
        Index('ix_24f1bf0', 'userid', 'delivered'),
        Index('ix_a6bafdfe', 'uuid_', 'companyid'),
        Index('ix_3dbb361a', 'userid', 'archived')
    )

    uuid_ = Column(String(75), index=True)
    usernotificationeventid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    userid = Column(BigInteger, index=True)
    type_ = Column(String(75))
    timestamp = Column(BigInteger)
    deliverby = Column(BigInteger)
    payload = Column(Text)
    archived = Column(Boolean)
    delivered = Column(Boolean)


class UsersGroup(Base):
    __tablename__ = 'users_groups'

    userid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    groupid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class UsersOrg(Base):
    __tablename__ = 'users_orgs'

    userid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    organizationid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class UsersRole(Base):
    __tablename__ = 'users_roles'

    userid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    roleid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class UsersTeam(Base):
    __tablename__ = 'users_teams'

    userid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    teamid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class UsersUsergroup(Base):
    __tablename__ = 'users_usergroups'

    usergroupid = Column(BigInteger, primary_key=True, nullable=False, index=True)
    userid = Column(BigInteger, primary_key=True, nullable=False, index=True)


class Usertracker(Base):
    __tablename__ = 'usertracker'

    usertrackerid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    modifieddate = Column(DateTime)
    sessionid = Column(String(200), index=True)
    remoteaddr = Column(String(75))
    remotehost = Column(String(75))
    useragent = Column(String(200))


class Usertrackerpath(Base):
    __tablename__ = 'usertrackerpath'

    usertrackerpathid = Column(BigInteger, primary_key=True)
    usertrackerid = Column(BigInteger, index=True)
    path_ = Column(Text)
    pathdate = Column(DateTime)


class Virtualhost(Base):
    __tablename__ = 'virtualhost'
    __table_args__ = (
        Index('ix_a083d394', 'companyid', 'layoutsetid', unique=True),
    )

    virtualhostid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    layoutsetid = Column(BigInteger)
    hostname = Column(String(75), unique=True)


class Vocabulary(Base):
    __tablename__ = 'vocabulary'

    vocabularyid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    description = Column(String(75))
    folksonomy = Column(Boolean)


class Webdavprop(Base):
    __tablename__ = 'webdavprops'
    __table_args__ = (
        Index('ix_97dfa146', 'classnameid', 'classpk', unique=True),
    )

    webdavpropsid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    props = Column(Text)


class Website(Base):
    __tablename__ = 'website'
    __table_args__ = (
        Index('ix_712bcd35', 'uuid_', 'companyid'),
        Index('ix_f960131c', 'companyid', 'classnameid', 'classpk'),
        Index('ix_4f0f0ca7', 'companyid', 'classnameid'),
        Index('ix_1aa07a6d', 'companyid', 'classnameid', 'classpk', 'primary_')
    )

    websiteid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger, index=True)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    url = Column(Text)
    typeid = Column(Integer)
    primary_ = Column(Boolean)
    uuid_ = Column(String(75), index=True)


class Wikinode(Base):
    __tablename__ = 'wikinode'
    __table_args__ = (
        Index('ix_b54332d6', 'companyid', 'status'),
        Index('ix_23325358', 'groupid', 'status'),
        Index('ix_920cd8b1', 'groupid', 'name', unique=True),
        Index('ix_e0e6d12c', 'uuid_', 'companyid'),
        Index('ix_7609b2ae', 'uuid_', 'groupid', unique=True)
    )

    uuid_ = Column(String(75), index=True)
    nodeid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger, index=True)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    description = Column(Text)
    lastpostdate = Column(DateTime)
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Wikipage(Base):
    __tablename__ = 'wikipage'
    __table_args__ = (
        Index('ix_899d3dfb', 'uuid_', 'groupid', unique=True),
        Index('ix_ba72b89a', 'groupid', 'nodeid', 'head', 'parenttitle', 'status'),
        Index('ix_5dc4bd39', 'uuid_', 'companyid'),
        Index('ix_9f7655da', 'nodeid', 'head', 'parenttitle', 'status'),
        Index('ix_2cd67c81', 'resourceprimkey', 'nodeid', 'version', unique=True),
        Index('ix_997eedd2', 'nodeid', 'title'),
        Index('ix_fbbe7c96', 'userid', 'nodeid', 'status'),
        Index('ix_941e429c', 'groupid', 'nodeid', 'status'),
        Index('ix_65e84af4', 'nodeid', 'head', 'parenttitle'),
        Index('ix_3d4af476', 'nodeid', 'title', 'version', unique=True),
        Index('ix_16e99b0a', 'groupid', 'nodeid', 'head'),
        Index('ix_1725355c', 'resourceprimkey', 'status'),
        Index('ix_e745ea26', 'nodeid', 'title', 'head'),
        Index('ix_546f2d5c', 'nodeid', 'status'),
        Index('ix_432f0ab0', 'nodeid', 'head', 'status'),
        Index('ix_94d1054d', 'resourceprimkey', 'nodeid', 'status'),
        Index('ix_bea33ab8', 'nodeid', 'title', 'status'),
        Index('ix_46eef3c8', 'nodeid', 'parenttitle'),
        Index('ix_1ecc7656', 'nodeid', 'redirecttitle'),
        Index('ix_caa451d6', 'groupid', 'userid', 'nodeid', 'status'),
        Index('ix_5ff21ce6', 'groupid', 'nodeid', 'title', 'head'),
        Index('ix_e1f55fb', 'resourceprimkey', 'nodeid', 'head'),
        Index('ix_e7f635ca', 'nodeid', 'head'),
        Index('ix_e0092ff0', 'groupid', 'nodeid', 'head', 'status'),
        Index('ix_40f94f68', 'nodeid', 'head', 'redirecttitle', 'status'),
        Index('ix_b771d67', 'resourceprimkey', 'nodeid')
    )

    uuid_ = Column(String(75), index=True)
    pageid = Column(BigInteger, primary_key=True)
    resourceprimkey = Column(BigInteger, index=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    nodeid = Column(BigInteger, index=True)
    title = Column(String(255))
    version = Column(Float(53))
    minoredit = Column(Boolean)
    content = Column(Text)
    summary = Column(Text)
    format = Column(String(75), index=True)
    head = Column(Boolean)
    parenttitle = Column(String(255))
    redirecttitle = Column(String(255))
    status = Column(Integer)
    statusbyuserid = Column(BigInteger)
    statusbyusername = Column(String(75))
    statusdate = Column(DateTime)


class Wikipageresource(Base):
    __tablename__ = 'wikipageresource'
    __table_args__ = (
        Index('ix_21277664', 'nodeid', 'title', unique=True),
    )

    uuid_ = Column(String(75), index=True)
    resourceprimkey = Column(BigInteger, primary_key=True)
    nodeid = Column(BigInteger)
    title = Column(String(255))


class Workflowdefinitionlink(Base):
    __tablename__ = 'workflowdefinitionlink'
    __table_args__ = (
        Index('ix_705b40ee', 'groupid', 'companyid', 'classnameid', 'classpk', 'typepk'),
        Index('ix_b6ee8c9e', 'groupid', 'companyid', 'classnameid'),
        Index('ix_1e5b9905', 'groupid', 'companyid', 'classnameid', 'classpk'),
        Index('ix_a4db1f0f', 'companyid', 'workflowdefinitionname', 'workflowdefinitionversion')
    )

    workflowdefinitionlinkid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    workflowdefinitionname = Column(String(75))
    workflowdefinitionversion = Column(Integer)
    classpk = Column(BigInteger)
    typepk = Column(BigInteger)


class Workflowinstancelink(Base):
    __tablename__ = 'workflowinstancelink'
    __table_args__ = (
        Index('ix_415a7007', 'groupid', 'companyid', 'classnameid', 'classpk'),
    )

    workflowinstancelinkid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger)
    userid = Column(BigInteger)
    username = Column(String(75))
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    classnameid = Column(BigInteger)
    classpk = Column(BigInteger)
    workflowinstanceid = Column(BigInteger)


class WsrpWsrpconsumer(Base):
    __tablename__ = 'wsrp_wsrpconsumer'

    wsrpconsumerid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger, index=True)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    url = Column(Text)
    wsdl = Column(Text)
    registrationcontextstring = Column(Text)
    registrationpropertiesstring = Column(Text)


class WsrpWsrpconsumerportlet(Base):
    __tablename__ = 'wsrp_wsrpconsumerportlet'
    __table_args__ = (
        Index('ix_d5f95908', 'wsrpconsumerid', 'portlethandle'),
    )

    wsrpconsumerportletid = Column(BigInteger, primary_key=True)
    companyid = Column(BigInteger)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    wsrpconsumerid = Column(BigInteger, index=True)
    name = Column(String(75))
    portlethandle = Column(Text)


class WsrpWsrpproducer(Base):
    __tablename__ = 'wsrp_wsrpproducer'

    wsrpproducerid = Column(BigInteger, primary_key=True)
    groupid = Column(BigInteger)
    companyid = Column(BigInteger, index=True)
    createdate = Column(DateTime)
    modifieddate = Column(DateTime)
    name = Column(String(75))
    portletids = Column(Text)
