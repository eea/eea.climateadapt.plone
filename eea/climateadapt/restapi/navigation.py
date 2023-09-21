from plone.restapi.interfaces import IExpandableElement, IPloneRestapiLayer
from plone.restapi.services.navigation.get import Navigation as BaseNavigation
from plone.restapi.services.navigation.get import \
    NavigationGet as BaseNavigationGet
from Products.CMFPlone.browser.navigation import \
    CatalogNavigationTabs as BaseCatalogNavigationTabs
from urlparse import urlparse
from zope.component import adapter
from zope.interface import Interface, implementer


# if '/mission' not in self.context.absolute_url(relative=True):
def is_outside_mission(context):
    bits = context.getPhysicalPath()
    if len(bits) > 3 and bits[3] == 'mission':
        return False

    return True


class CatalogNavigationTabs(BaseCatalogNavigationTabs):
    def _getNavQuery(self):
        query = super(CatalogNavigationTabs, self)._getNavQuery()

        if not is_outside_mission(self.context):
            return query

        query['show_in_top_level'] = True

        return query


@implementer(IExpandableElement)
@adapter(Interface, IPloneRestapiLayer)
class Navigation(BaseNavigation):
    def __call__(self, expand=False):
        if self.request.form.get("expand.navigation.depth", False):
            # self.depth = int(self.request.form["expand.navigation.depth"])

            if is_outside_mission(self.context):
                self.depth = 8
            else:
                self.depth = int(self.request.form["expand.navigation.depth"])
        else:
            self.depth = 1

        result = {"navigation": {"@id": self.context.absolute_url() + "/@navigation"}}
        if not expand:
            return result

        result["navigation"]["items"] = self.build_tree(self.navtree_path)
        return result

    def customize_entry(self, entry, brain):
        entry['brain'] = brain
        if hasattr(brain, 'remoteUrl'):
            entry['path'] = urlparse(brain.remoteUrl).path
            entry['@id'] = brain.remoteUrl
        return entry

    def render_item(self, item, path):
        sub = self.build_tree(item["path"], first_run=False)

        item.update({"items": sub})

        if "path" in item:
            del item["path"]

        if 'brain' in item:
            del item['brain']

        return item


class NavigationGet(BaseNavigationGet):
    def reply(self):
        navigation = Navigation(self.context, self.request)
        return navigation(expand=True)["navigation"]
