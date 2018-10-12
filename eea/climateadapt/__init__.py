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

# monkey patch plone.dexterity.content.Container
from plone.dexterity.content import Container
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
import Products.CMFCore.permissions
# Change permission for manage_pasteObjects to "Add portal content"
# See https://dev.plone.org/ticket/9177

# TODO: Find a way to do this without patching __ac_permissions__ directly

def drop_protected_attr_from_ac_permissions(attribute, classobj):
    new_mappings = []
    for mapping in Container.__ac_permissions__:
        perm, attrs = mapping
        if not attribute in attrs:
            new_mappings.append(mapping)
        else:
            modified_attrs = tuple([a for a in attrs if not a == attribute])
            modified_mapping = (perm, modified_attrs)
            new_mappings.append(modified_mapping)
    classobj.__ac_permissions__ = tuple(new_mappings)

drop_protected_attr_from_ac_permissions('manage_pasteObjects', Container)
sec = ClassSecurityInfo()
sec.declareProtected(Products.CMFCore.permissions.AddPortalContent,
                    'manage_pasteObjects')
sec.apply(Container)
InitializeClass(Container)


def initialize(context):

    context.registerClass(roleplugin.CityMayorUserFactory,
                          permission=add_user_folders,
                          constructors=(
                              roleplugin.manage_addCityMayorUserFactoryForm,
                              roleplugin.manage_addCityMayorUserFactory),
                          visibility=None
                          )


from eea.notifications import utils


LABELS = {}


# Monkey eea.notifications get_tags
def get_tags_cca(obj):
    try:
        tags = obj.keywords
    except Exception:
        tags = ()
    return tags


utils.get_tags = get_tags_cca
