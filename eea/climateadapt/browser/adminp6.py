from Products.Five.browser import BrowserView


class GoPDB(BrowserView):
    def __call__(self):
        import pdb

        pdb.set_trace()
        x = self.context.Creator()
