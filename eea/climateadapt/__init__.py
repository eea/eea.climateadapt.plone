import OFS
import transaction
# import collective.cover.config
from zope.i18nmessageid import MessageFactory as BaseMessageFactory

import Products.CMFCore.permissions
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
# from eea.notifications import utils
from plone.dexterity.content import Container
from plone.i18n import normalizer
from App.ZApplication import ZApplicationWrapper


class UnicodeMessageFactory(BaseMessageFactory):
    def __call__(self, *args, **kwds):
        unicode_args = [str(s) for s in args]
        # __import__("pdb").set_trace()
        return super(UnicodeMessageFactory, self).__call__(*unicode_args, **kwds)


# Set up the i18n message factory for our package
CcaMenuMessageFactory = UnicodeMessageFactory("eea.climateadapt.menu")
CcaAdminMessageFactory = UnicodeMessageFactory("eea.climateadapt.admin")
MessageFactory = UnicodeMessageFactory("eea.climateadapt")

# Change permission for manage_pasteObjects to "Add portal content"
# See https://dev.plone.org/ticket/9177

# TODO: Find a way to do this without patching __ac_permissions__ directly
# monkey patch plone.dexterity.content.Container
# patch collective.cover grid system
# collective.cover.config.DEFAULT_GRID_SYSTEM = "bootstrap3"

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


LABELS = {}


# Monkey eea.notifications get_tags
# def get_tags_cca(obj):
#     try:
#         tags = obj.keywords
#     except Exception:
#         tags = ()
#     return tags


# utils.get_tags = get_tags_cca

# Raven repr monkey patch #129327


def ZApplicationWrapper__repr__(self):
    """ZApplicationWrapper has no __repr__ because it does not inherit
    from object.
    For having stack locals in sentry, the raven client tries to make
    repr() for each object, which fails with the ZApplicationWrapper
    because there is no implementation.
    Therefore we add the __repr__ to the ZApplicationWrapper class.
    """
    mod = self.__class__.__module__
    cls = self.__class__.__name__
    mem = "0x" + hex(id(self))[2:].zfill(8).upper()
    return "<{0}.{1} instance at {2}>".format(mod, cls, mem)


ZApplicationWrapper.__repr__ = ZApplicationWrapper__repr__


# def isLinked(obj):
#     """check if the given content object is linked from another one
#     WARNING: this function can be time consuming !!
#         It deletes the object in a subtransaction that is rollbacked.
#         In other words, the object is kept safe.
#         Nevertheless, this implies that it also deletes recursively
#         all object's subobjects and references, which can be very
#         expensive.
#     """
#     # first check to see if link integrity handling has been enabled at all
#     # and if so, if the removal of the object was already confirmed, i.e.
#     # while replaying the request;  unfortunately this makes it necessary
#     # to import from plone.app.linkintegrity here, hence the try block...
#     try:
#         from plone.app.linkintegrity.interfaces import ILinkIntegrityInfo

#         info = ILinkIntegrityInfo(obj.REQUEST)
#     except (ImportError, TypeError):
#         # if p.a.li isn't installed the following check can be cut short...
#         return False
#     if not info.integrityCheckingEnabled():
#         return False
#     if info.isConfirmedItem(obj):
#         return True
#     # otherwise, when not replaying the request already, it is tried to
#     # delete the object, making it possible to find out if it was referenced,
#     # i.e. in case a link integrity exception was raised
#     linked = False
#     parent = obj.aq_inner.aq_parent
#     try:
#         savepoint = transaction.savepoint()
#         parent.manage_delObjects(obj.getId())
#     except OFS.ObjectManager.BeforeDeleteException:
#         linked = True
#     except Exception:  # ignore other exceptions, not useful to us at this point
#         pass
#     finally:
#         savepoint.rollback()
#     return linked
