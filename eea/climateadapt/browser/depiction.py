from eea.depiction.browser.dexterity import DexterityImageView


class CCAContentDepictionView(DexterityImageView):
    """ Get cover image from folder contents
    """

    @property
    def fieldname(self):
        if getattr(self.context, 'logo', None):
            return 'logo'

        return "image"

    @property
    def img(self):
        """
        """
        return self.context
