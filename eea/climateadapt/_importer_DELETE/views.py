from Products.Five.browser import BrowserView
from collections import defaultdict
from eea.climateadapt._importer.utils import get_template_for_layout
from eea.climateadapt._importer.utils import create_folder_at
from eea.climateadapt._importer.utils import parse_settings
from eea.climateadapt._importer.utils import strip_xml
from eea.climateadapt._importer import import_aceitems as base_import_aceitems
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
            if layout.type_ in ['control-panel']:
                # we skip control panel pages
                continue

            settings = parse_settings(layout.typesettings)

            if layout.type_ == 'link_to_layout':
                llid = int(settings['linkToLayoutId'][0])
                try:
                    ll = session.query(sql.Layout).filter_by(layoutid=llid).one()
                except:
                    print(("Got error on layout", layout.friendlyurl))
                    continue
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
                print(("Couldn't import layout %s", layout.friendlyurl))
            if cover:
                cover._imported_comment = \
                    "Imported from layout {0}".format(layout.layoutid)
                print(("Created cover at %s" % cover.absolute_url()))

    def import_dlentries(self):
        from eea.climateadapt._importer import import_dlfileentry
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        imported = []

        #import pdb; pdb.set_trace()
        to_import = session.query(sql.Dlfileentry)
        id = self.request.form.get('id')
        if id:
            to_import = to_import.filter_by(fileentryid=int(id))

        for dlfileentry in to_import:
            f = import_dlfileentry(dlfileentry, site['repository'])
            if f is None:
                continue
            link = "<a href='{0}'>{1}</a>".format(f.absolute_url(), f.getId())
            imported.append(link)

        return "<br/>".join(imported)

    def import_aceitems(self):
        from eea.climateadapt._importer import import_aceitem
        from eea.climateadapt._importer import sql
        from eea.climateadapt._importer.tweak_sql import fix_relations

        session = self._make_session()
        eea.climateadapt._importer.session = session
        fix_relations(session)
        site = self.context

        id = self.request.form.get('id')
        if id:
            aceitem = session.query(sql.AceAceitem).\
                filter_by(aceitemid=int(id)).one()
            obj = import_aceitem(aceitem, site)
            return self.request.response.redirect(obj.absolute_url())

        base_import_aceitems(session, site)
        return 'done'

    def import_casestudy(self):
        from eea.climateadapt._importer import import_casestudy
        from eea.climateadapt._importer import import_adaptationoption
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        if 'casestudy' not in site.contentIds():
            site.invokeFactory("Folder", 'casestudy')
            site['casestudy'].edit(title='Case Studies')

        to_import = session.query(sql.AceMeasure)
        id = self.request.form.get('id')
        if id:
            to_import = to_import.filter_by(measureid=int(id))

        # TODO: fix this code
        imported = []
        for acemeasure in to_import:
            if acemeasure.mao_type == 'A':
                obj = import_casestudy(acemeasure, site['casestudy'])
                imported.append(obj)
                print(("Imported Case Study {0} from id {1}".format(
                    obj.absolute_url(), acemeasure.measureid)))
            else:
                obj = import_adaptationoption(acemeasure,
                                              site['metadata']['adaptation-options'])
                imported.append(obj)
                print(("Imported Adaptation Option {0} from id {1}".format(
                    obj.absolute_url(), acemeasure.measureid)))

        if imported:
            return self.request.response.redirect(imported[0].absolute_url())
        else:
            return "Nothing to import"

    def import_fix_casestudies(self):
        from eea.climateadapt._importer import fix_casestudy_images
        fix_casestudy_images(self.context)

    def import_projects(self):
        from eea.climateadapt._importer import import_aceproject
        from eea.climateadapt._importer import sql

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        if 'aceprojects' not in site.contentIds():
            site.invokeFactory("Folder", 'aceprojects')
            site['aceprojects'].edit(title='Projects')

        to_import = session.query(sql.AceProject)
        id = self.request.form.get('id')
        if id:
            to_import = to_import.filter_by(projectid=int(id))

        imported = []
        for project in to_import:
            obj = import_aceproject(project, site['aceprojects'])
            imported.append(obj)
            print(("Imported Project {0} from id {1}".format(
                obj.absolute_url(), project.projectid)))
        if imported:
            return self.request.response.redirect(imported[0].absolute_url())
        else:
            return "Nothing to import"

    def import_journal_articles(self):
        from eea.climateadapt._importer import import_journal_articles

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context

        import_journal_articles(site)

        return "Done"

    def import_city_profile(self):
        from eea.climateadapt._importer import import_city_profiles

        session = self._make_session()
        eea.climateadapt._importer.session = session
        site = self.context
        cities = import_city_profiles(site)
        return "Imported {0} cities".format(len(cities))

    def import_detect_richtext(self):
        from eea.climateadapt._importer.utils import detect_richtext_fields
        session = self._make_session()
        eea.climateadapt._importer.session = session
        #site = self.context
        detect_richtext_fields(session)
        return "done"

    def import_portlet_preferences(self):
        from eea.climateadapt._importer import sql
        import lxml.etree
        import lxml.html

        session = self._make_session()
        eea.climateadapt._importer.session = session

        saportlets = session.query(sql.Portletpreference)
        for portlet in saportlets:
            if portlet.preferences is not None:
                e = lxml.etree.fromstring(portlet.preferences)
                prefs = {}
                for pref in e.xpath('//preference'):
                    name = str(pref.find('name').text)
                    values = pref.findall('value')
                    if len(values) > 1:
                        print((len(values), name, portlet.portletid))
                    res = []
                    for node in values:
                        try:
                            value = node.text
                        except Exception:
                            continue
                        if value is not None:
                            res.append(str(value))
                    if len(res) == 0:
                        prefs[name] = None
                    elif len(res) == 1:
                        prefs[name] = res[0]
                    else:
                        prefs[name] = res

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

    def site_url(self):
        return getSite().absolute_url()


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
