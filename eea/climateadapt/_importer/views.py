from Products.Five.browser import BrowserView
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import register
import eea.climateadapt._importer
import os


class SingleImporterView(BrowserView):

    def _make_session(self):
        engine = create_engine(os.environ.get("DB"))
        Session = scoped_session(sessionmaker(bind=engine))
        register(Session, keep_session=True)
        session = Session()
        return session

    def __call__(self):
        from eea.climateadapt._importer import import_layout
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        layoutid = int(self.request.form.get('layoutid'))
        layout = session.query(sql.Layout).filter_by(privatelayout=False,
                                                     layoutid=layoutid).one()
        import pdb; pdb.set_trace()
        import_layout(layout, site)

        return "done"


class GoToPDB(BrowserView):
    def __call__(self):
        import pdb; pdb.set_trace()
        return "done"
