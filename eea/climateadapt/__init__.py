from AccessControl.Permissions import add_user_folders
from eea.climateadapt.mayorsadapt import roleplugin
from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('eea.climateadapt')

# patch collective.cover grid system
import collective.cover.config
collective.cover.config.DEFAULT_GRID_SYSTEM = 'bootstrap3'

# patch max length URL fragment generation, makes for shorter IDs for content
from plone.i18n import normalizer
normalizer.MAX_URL_LENGTH = 100


def initialize(context):

    context.registerClass(roleplugin.CityMayorUserFactory,
                          permission=add_user_folders,
                          constructors=(
                              roleplugin.manage_addCityMayorUserFactoryForm,
                              roleplugin.manage_addCityMayorUserFactory),
                          visibility=None
                          )
