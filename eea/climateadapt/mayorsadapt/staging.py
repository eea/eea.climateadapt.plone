#from zope.interface import providedBy, noLongerProvides, alsoProvides
from AccessControl import getSecurityManager
from eea.climateadapt.city_profile import ICityProfile
from eea.climateadapt.city_profile import ICityProfileStaging
from plone.app.iterate.permissions import CheckinPermission
from plone.app.stagingbehavior.browser.control import Control
from plone.app.stagingbehavior.interfaces import IStagingSupport
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.behavior import DexterityBehaviorAssignable
from plone.dexterity.schema import SCHEMA_CACHE
from zope.component import adapter
from zope.interface import implementer
from Products.Five import BrowserView


class IterateControl(Control):
    """Information about whether iterate can operate.

    This is a public view, referenced in action condition expressions.
    """

    def checkin_allowed(self):
        """ Check if a checkin is allowed.
            Conditions:
            - provides IIterateAware
            - is not baseline
            - is the working copy
            - is versionable
            - user should have ModifyPortalContent permission
        """
        allowed = super(IterateControl, self).checkin_allowed()
        checkPermission = getSecurityManager().checkPermission
        print "check permission"
        return allowed and checkPermission(CheckinPermission, self.context)


@implementer(IBehaviorAssignable)
@adapter(ICityProfile)
class CityProfileBehaviorAssignable(DexterityBehaviorAssignable):
    """ Custom BehaviorAssignable adapter.

    We want to reorder the behavior markers so that ICityProfileStaging is the
    first one.
    """

    def enumerateBehaviors(self):
        res = []
        _sb = None
        _cpb = None
        behvs = SCHEMA_CACHE.behavior_registrations(self.context.portal_type)
        for b in behvs:
            if b.interface is ICityProfileStaging:
                _cpb = b
            elif b.interface is IStagingSupport:
                _sb = b
            else:
                res.append(b)

        res = [_cpb, _sb] + res

        for behavior in res:
            yield behavior
