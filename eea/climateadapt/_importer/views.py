from Products.Five.browser import BrowserView
from collections import defaultdict
from eea.climateadapt._importer.utils import get_template_for_layout
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.component.hooks import getSite
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

    def import_layout(self):
        from eea.climateadapt._importer import import_layout
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        uuid = self.request.form.get('uuid')
        layout = session.query(sql.Layout).filter_by(privatelayout=False,
                                                     uuid_=uuid).one()
        cover = import_layout(layout, site)
        if cover:
            return self.request.response.redirect(cover.absolute_url())

        return "no cover?"

    def import_dlentries(self):
        from eea.climateadapt._importer import import_dlfileentry
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        imported = []

        for dlfileentry in session.query(sql.Dlfileentry):
            f = import_dlfileentry(dlfileentry, site['repository'])
            if f is None:
                continue
            link = "<a href='{0}'>{1}</a>".format(f.absolute_url(), f.getId())
            imported.append(link)

        return "<br/>".join(imported)

    def __call__(self):
        _type = self.request.form.get('type', 'layout')

        importer = getattr(self, 'import_' + _type)
        return importer()


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
            self.options[template].append((layout.friendlyurl, layout.uuid_))

        return self.index()

    def import_url(self, uuid):
        site = getSite()
        return site.absolute_url() + "/layout_importer?uuid=" + uuid
        pass

