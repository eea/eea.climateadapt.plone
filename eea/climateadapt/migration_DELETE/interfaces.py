from zope.interface import Interface


class IMigrateToVolto(Interface):
    """Migrate content to Volto blocks"""


class IMigrateTile(Interface):
    """Migrate a collective.cover tile"""
