from zope.interface import Attribute, Interface


class ITranslationsStorage(Interface):
    """ Provide storage (as a mapping) for translations
    Keys will be the language codes
    """


class ITranslationContext(Interface):
    """
    """

    language = Attribute("Language code")
