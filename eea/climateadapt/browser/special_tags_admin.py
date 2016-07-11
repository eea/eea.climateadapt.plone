from Products.Five.browser import BrowserView
import json


class SpecialTagsView(BrowserView):
    """ Custom view for administration of special tags
    """

    def __call__(self):
        self.sp_tags = []

        for tag in self.context.portal_catalog.uniqueValuesFor('special_tags'):
            self.sp_tags.append(tag)

        return self.index()


class SpecialTagsObjects (BrowserView):
    """ Gets the links for the special tags that we get in the request
    """

    def __call__(self):
        tag = self.request.form['special_tags'].decode('utf-8')
        tag_obj = [b.getURL() + '/edit' for b in
                   self.context.portal_catalog.searchResults(special_tags=tag)]
        return json.dumps(tag_obj)
