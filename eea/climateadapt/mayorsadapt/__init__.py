""" Utilities for mayors adapt functionality
"""

from Products.PluggableAuthService import registerMultiPlugin
import roleplugin

registerMultiPlugin(roleplugin.TokenBasedRolesManager.meta_type)

