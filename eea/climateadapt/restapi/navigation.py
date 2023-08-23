from Products.CMFPlone.browser.navigation import \
    CatalogNavigationTabs as BaseCatalogNavigationTabs


class CatalogNavigationTabs(BaseCatalogNavigationTabs):
    def _getNavQuery(self):
        query = super(CatalogNavigationTabs, self)._getNavQuery()

        if '/mission/' not in self.context.absolute_url(relative=True):
            query['show_in_top_level'] = True

        return query
