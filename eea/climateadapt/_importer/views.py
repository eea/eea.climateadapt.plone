from Products.Five.browser import BrowserView


class SingleImporterView(BrowserView):
    def __call__(self):
        from eea.climateadapt._importer import import_template_ace_layout_3
        from eea.climateadapt._importer import session
        from eea.climateadapt._importer import sql

        site = self.context

        layoutid = int(self.request.form.get('layoutid'))

        layout = session.query(sql.Layout).filter_by(privatelayout=False,
                                                     layoutid=layoutid).one()
        import_template_ace_layout_3(layout, site)
