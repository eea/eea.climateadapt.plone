from Products.Five.browser import BrowserView


class RedirectToSearchView (BrowserView):
    """ Custom view for /content """

    def __call__(self):
        type_name = self.context.getProperty('search_type_name', '')
        url = '/data-and-downloads'
        if type_name:
            url += '#searchtype=' + type_name

        return self.request.response.redirect(url)

