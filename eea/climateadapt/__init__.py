import collective.cover.config
from zope.i18nmessageid import MessageFactory

import Products.CMFCore.permissions
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import add_user_folders
from eea.climateadapt.mayorsadapt import roleplugin
from eea.notifications import utils
from plone.dexterity.content import Container
from plone.i18n import normalizer

# Set up the i18n message factory for our package
MessageFactory = MessageFactory("eea.climateadapt")

# Change permission for manage_pasteObjects to "Add portal content"
# See https://dev.plone.org/ticket/9177

# TODO: Find a way to do this without patching __ac_permissions__ directly
# monkey patch plone.dexterity.content.Container
# patch collective.cover grid system
collective.cover.config.DEFAULT_GRID_SYSTEM = "bootstrap3"

# patch max length URL fragment generation, makes for shorter IDs for content
normalizer.MAX_URL_LENGTH = 100


def drop_protected_attr_from_ac_permissions(attribute, classobj):
    new_mappings = []
    for mapping in Container.__ac_permissions__:
        perm, attrs = mapping
        if attribute not in attrs:
            new_mappings.append(mapping)
        else:
            modified_attrs = tuple([a for a in attrs if not a == attribute])
            modified_mapping = (perm, modified_attrs)
            new_mappings.append(modified_mapping)
    classobj.__ac_permissions__ = tuple(new_mappings)


drop_protected_attr_from_ac_permissions("manage_pasteObjects", Container)
sec = ClassSecurityInfo()
sec.declareProtected(
    Products.CMFCore.permissions.AddPortalContent, "manage_pasteObjects"
)
sec.apply(Container)
InitializeClass(Container)


def initialize(context):

    context.registerClass(
        roleplugin.CityMayorUserFactory,
        permission=add_user_folders,
        constructors=(
            roleplugin.manage_addCityMayorUserFactoryForm,
            roleplugin.manage_addCityMayorUserFactory,
        ),
        visibility=None,
    )


LABELS = {}


# Monkey eea.notifications get_tags
def get_tags_cca(obj):
    try:
        tags = obj.keywords
    except Exception:
        tags = ()
    return tags


utils.get_tags = get_tags_cca
