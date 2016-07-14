from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.directives import form
from z3c.form import button
from zope import schema
import json


class KeywordsAdminView (BrowserView):
    """ Custom view for the administration of keywords
    """

    def __call__(self):
        self.keyword = []

        for key in self.context.portal_catalog.uniqueValuesFor('keywords'):
            self.keyword.append(key)

        return self.index()

    def get_keyword_length(self, key):
        catalog = self.context.portal_catalog._catalog
        return len(catalog.indexes['keywords']._index[key])


class KeywordObjects (BrowserView):
    """ Gets the links for the keyword that we get in the request
    """

    def __call__(self):
        key = self.request.form['keyword'].decode('utf-8')
        key_obj = [b.getURL() + '/edit' for b in
                   self.context.portal_catalog.searchResults(keywords=key)]
        return json.dumps(key_obj)


class IMainNavigationMenu(form.Schema):
    menu = schema.Text(title=u"Menu structure text", required=True)


class MainNavigationMenuEdit(form.SchemaForm):
    """ A page to edit the main site navigation menu
    """

    schema = IMainNavigationMenu
    ignoreContext = False

    label = u"Fill in the content of the main menu"
    description = u"""This should be a structure for the main menu. Use a single
    empty line to separate main menu entries. All lines after the main menu
    entry, and before an empty line, will form entries in that section menu. To
    create a submenu for a section, start a line with a dash (-).  Links should
    start with a slash (/)."""

    # TODO: validation!

    @property
    def ptool(self):
        return getToolByName(self.context,
                              'portal_properties')['site_properties']

    def getContent(self):
        content = {'menu': self.ptool.getProperty('main_navigation_menu')}
        return content

    @button.buttonAndHandler(u"Save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.ptool._updateProperty('main_navigation_menu', data['menu'])

        self.status = u"Saved, please check."


class ForceUnlock(BrowserView):
    """ Forcefully unlock a content item
    """

    def __call__(self):
        annot = getattr(self.context, '__annotations__', {})

        if hasattr(self.context, '_dav_writelocks'):
            del self.context._dav_writelocks
            self.context._p_changed = True
        if 'plone.locking' in annot:
            del annot['plone.locking']

            self.context._p_changed = True
            annot._p_changed = True

        url = self.context.absolute_url()
        props_tool = getToolByName(self.context, 'portal_properties')
        if props_tool:
            types_use_view = \
                props_tool.site_properties.typesUseViewActionInListings
            if self.context.portal_type in types_use_view:
                url += '/view'

        return self.request.RESPONSE.redirect(url)
