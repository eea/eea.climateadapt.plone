""" Utilities for mayors adapt functionality
"""

from Products.PluggableAuthService import registerMultiPlugin
from . import roleplugin

registerMultiPlugin(roleplugin.CityMayorUserFactory.meta_type)
