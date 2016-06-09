from Products.Five.browser import BrowserView
#from zope.interface import Interface
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
