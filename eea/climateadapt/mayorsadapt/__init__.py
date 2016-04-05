""" Utilities for mayors adapt functionality
"""

from Products.PluggableAuthService import registerMultiPlugin
import roleplugin

registerMultiPlugin(roleplugin.CityMayorUserFactory.meta_type)
