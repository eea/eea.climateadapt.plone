from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.behavior import DexterityBehaviorAssignable
from plone.restapi.behaviors import IBlocks
from zope.component import adapter, getUtility
from zope.interface import implementer
from eea.climateadapt.interfaces import IDiscodataVersionMarker
from plone.supermodel import model
from zope.schema import TextLine
from zope.interface import provider
from eea.climateadapt import CcaAdminMessageFactory as _


@provider(IFormFieldProvider)
class IDiscodataVersion(model.Schema, IBlocks):
    """IDiscodataVersion Interface"""

    discodata_version = TextLine(
        title=_("Discodata version"),
        description=_("Sandbox version for discodata"),
        required=False,
    )


@implementer(IBehaviorAssignable)
@adapter(IDiscodataVersionMarker)
class DiscodataVersionBehaviorAssignable(DexterityBehaviorAssignable):
    """Custom assignable that adds the discodata behavior
    if the marker is present.
    """

    def enumerateBehaviors(self):
        # import pdb
        # pdb.set_trace()
        # Yield default behaviors from FTI
        for behavior in super(
            DiscodataVersionBehaviorAssignable, self
        ).enumerateBehaviors():
            yield behavior

        # Also yield our custom behavior
        behavior = getUtility(IBehavior, name="eea.climateadapt.discodata_version")
        yield behavior
