""" Views to be used by tiles.

It helps to separate the tiles from the views, those views can be easier
developed and tested.
"""


from Products.Five.browser import BrowserView


class AceContentSearch(BrowserView):
    """ A view to show an AceContet "portlet" search
    """
