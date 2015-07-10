from eea.climateadapt._importer import sqlschema as sql
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import create_engine
from zope.sqlalchemy import register
import transaction
import os


def run_importer(session):
    print session.query(sql.Account).count()
    sql.AceAceitem.company = relationship(sql.Company,
                                          foreign_keys=sql.AceAceitem.companyid,
                                          primaryjoin="and_(Company.companyid==AceAceitem.companyid)")
    item = session.query(sql.AceAceitem).first()
    print item.company
    import pdb; pdb.set_trace()


def main():
    engine = create_engine(os.environ.get("DB"))
    Session = scoped_session(sessionmaker(bind=engine))
    register(Session, keep_session=True)
    session = Session()
    run_importer(session)
    transaction.commit()
    return
