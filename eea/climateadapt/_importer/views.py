from Products.Five.browser import BrowserView
from collections import defaultdict
from eea.climateadapt._importer.utils import get_template_for_layout
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
        cover = import_layout(layout, site)
        if cover:
            return "<a href='" + cover.absolute_url() + "'>cover</a>"

        return "done"


class GoToPDB(BrowserView):
    def __call__(self):
        import pdb; pdb.set_trace()
        return "done"


class MapOfLayouts(SingleImporterView):
    def __call__(self):
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session

        self.options = defaultdict(list)

        for layout in session.query(sql.Layout).filter_by(privatelayout=False):
            template = get_template_for_layout(layout)
            self.options[template].append((layout.friendlyurl, layout.layoutid))

        return self.index()

