from AccessControl import getSecurityManager
from plone.app.iterate.browser.control import Control
from plone.app.iterate.permissions import CheckinPermission


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
        return allowed and checkPermission(CheckinPermission, self.context)
