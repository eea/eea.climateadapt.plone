from Products.Five.browser import BrowserView
from collections import defaultdict
from eea.climateadapt._importer.utils import get_template_for_layout
from eea.climateadapt._importer.utils import create_folder_at
from eea.climateadapt._importer.utils import parse_settings
from eea.climateadapt._importer.utils import strip_xml
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.component.hooks import getSite
from zope.sqlalchemy import register
import eea.climateadapt._importer
import os


class SingleImporterView(BrowserView):
    """ Registered as /@@layout_importer

    Call with one of
    * ?uuid=<uuid>
    * layout=<layoutid>
    * type=casestudy[&id=<measureid>]
    * type=aceitems

    """

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
        if uuid:
            layout = session.query(sql.Layout).filter_by(privatelayout=False,
                                                         uuid_=uuid).one()
        else:
            id = self.request.form.get('layout')
            layout = session.query(sql.Layout).filter_by(privatelayout=False,
                                                         layoutid=id).one()

        cover = import_layout(layout, site)
        if cover:
            return self.request.response.redirect(cover.absolute_url())

        return "no cover?"

    def import_layout_type(self):
        """ Allows importing a batch of layouts by their template name
        """
        from eea.climateadapt._importer import import_layout
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        template = self.request.form.get('template', '').strip()
        if not template:
            raise ValueError("Please provide a template")

        for layout in session.query(sql.Layout).filter_by(privatelayout=False):
            if layout.type_ in [u'control-panel']:
                # we skip control panel pages
                continue

            settings = parse_settings(layout.typesettings)

            if layout.type_ == u'link_to_layout':
                llid = int(settings['linkToLayoutId'][0])
                try:
                    ll = session.query(sql.Layout).filter_by(layoutid=llid).one()
                except:
                    import pdb; pdb.set_trace()
                this_url = layout.friendlyurl
                child_url = ll.friendlyurl
                folder = create_folder_at(site, this_url)
                folder.setLayout(child_url.split('/')[-1])
                folder.title = strip_xml(ll.name)
                continue

            try:
                layout_template = settings['layout-template-id'][0]
            except:
                import pdb; pdb.set_trace()
            if not layout_template == template:
                continue

            try:
                cover = import_layout(layout, site)
            except:
                print "Couldn't import layout %s", layout.friendlyurl
            if cover:
                cover._imported_comment = \
                    "Imported from layout {0}".format(layout.layoutid)
                print "Created cover at %s" % cover.absolute_url()


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

    def import_aceitems(self):
        from eea.climateadapt._importer import import_aceitem
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        if 'content' not in site.contentIds():
            site.invokeFactory("Folder", 'content')

        for aceitem in session.query(sql.AceAceitem):
            if aceitem.datatype in ['ACTION', 'MEASURE']:
                # TODO: log and solve here
                continue
            import_aceitem(aceitem, site['content'])

    def import_casestudy(self):
        from eea.climateadapt._importer import import_casestudy as importer
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        if 'casestudy' not in site.contentIds():
            site.invokeFactory("Folder", 'casestudy')

        to_import = session.query(sql.AceMeasure)
        id = self.request.form.get('id')
        if id:
            to_import = to_import.filter_by(measureid=int(id))

        for acemeasure in to_import:
            if acemeasure.mao_type == 'A':
                obj = importer(acemeasure, site['casestudy'])
                print "Imported ", obj.absolute_url()

    def __call__(self):
        _type = self.request.form.get('type', 'layout')
        debug = self.request.form.get('debug')
        if debug:
            import pdb; pdb.set_trace()

        importer = getattr(self, 'import_' + _type)
        return importer() or "done"


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

    def aceimport_url(self):
        site = getSite()
        return site.absolute_url() + "/layout_importer?type=aceitems"

    def dlimport_url(self):
        site = getSite()
        return site.absolute_url() + "/layout_importer?type=dlentries"

    def caseimport_url(self):
        site = getSite()
        return site.absolute_url() + "/layout_importer?type=casestudy"

    def ast_import_url(self):
        site = getSite()
        return site.absolute_url() + "/layout_importer?type=layout_type&template=ast"


class FacetedImporter(BrowserView):
    def __call__(self):
        from eea.climateadapt._importer.utils import make_faceted

        if 'submit' in self.request.form:
            site = self.context

            form = self.request.form
            location = form['location']
            xmlfilename = form['xmlfilename']
            layout = form['layout']

            faceted = make_faceted(site, location, xmlfilename, layout)
            return self.request.response.redirect(faceted.absolute_url())
        else:
            return self.index()
