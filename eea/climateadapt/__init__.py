from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('eea.climateadapt')

# patch collective.cover grid system

import collective.cover.config


collective.cover.config.DEFAULT_GRID_SYSTEM = 'bootstrap3'
