from zope.component import queryMultiAdapter  # getMultiAdapter,
from zope.publisher.interfaces import NotFound

from eea.depiction.browser.dexterity import DexterityImageView


class CCAContentDepictionView(DexterityImageView):
    """ Get cover image from folder contents
    """

    _field = "image"

    @property
    def img(self):
        """
        """
        return self.context

    @property
    def field(self):
        """ Image field
        """

        return getattr(self.context, self._field, None)

    def __call__(self, scalename='thumb'):
        if not self.display(scalename):
            raise NotFound(self.request, scalename)

        scaleview = queryMultiAdapter((self.img, self.request), name='images')
        scale = scaleview.scale(self._field, scale=scalename)

        return scale or ""
