from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import register
import transaction


def run_importer(session):
    pass


def main():
    engine = ""
    Session = scoped_session(sessionmaker(bind=engine))
    register(Session, keep_session=True)
    session = Session()
    run_importer(session)
    transaction.commit()
    return
