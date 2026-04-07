# A copy of plone.shortname from
# https://github.com/plone/plone.app.dexterity/blob/fe92c804c545e4c218d60906e8ce5f5ec6cdfd95/plone/app/dexterity/behaviors/id.py

import transaction
from Acquisition import aq_base, aq_inner, aq_parent
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.locking.interfaces import ILockable
from plone.supermodel import model
from zope import schema
from zope.container.interfaces import INameChooser

# from zope.interface import alsoProvides
from zope.interface import provider

from eea.climateadapt import CcaAdminMessageFactory as _

# from plone.app.multilingual.dx.interfaces import ILanguageIndependentField


@provider(IFormFieldProvider)
class IShortName(model.Schema):
    # model.fieldset(
    #     "settings",
    #     label=_("Settings"),
    #     fields=["id"],
    # )

    id = schema.ASCIILine(
        title=_("Short name"),
        description=_("This name will be displayed in the URL."),
        required=False,
    )
    directives.write_permission(id="cmf.AddPortalContent")


# alsoProvides(IShortName["id"], ILanguageIndependentField)


class ShortName(object):
    def __init__(self, context):
        self.context = context

    def _get_id(self):
        try:
            return self.context.getId()
        except AttributeError:
            return ""

    def _set_id(self, value):
        if not value:
            return
        context = aq_inner(self.context)
        parent = aq_parent(context)
        if parent is None:
            # Object hasn't been added to graph yet; just set directly
            context.id = value
            return
        new_id = INameChooser(parent).chooseName(value, context)
        if getattr(aq_base(context), "id", None):
            transaction.savepoint()
            locked = False
            lockable = ILockable(context, None)
            if lockable is not None and lockable.locked():
                locked = True
                lockable.unlock()
            parent.manage_renameObject(context.getId(), new_id)
            if locked:
                lockable.lock()
        else:
            context.id = new_id

    id = property(_get_id, _set_id)
