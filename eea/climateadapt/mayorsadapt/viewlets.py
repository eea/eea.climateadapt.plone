import tokenlib
from tokenlib.errors import (ExpiredTokenError, InvalidSignatureError,
                             MalformedTokenError)
from eea.climateadapt.city_profile import TOKENID
from eea.climateadapt.mayorsadapt.roleplugin import is_citymayor_visitor
from plone.api.content import get_state
from plone.app.layout.viewlets import ViewletBase
from plone.app.stagingbehavior.utils import get_baseline, get_working_copy
from zope.annotation.interfaces import IAnnotations
from zope.globalrequest import getRequest


class EditMenuViewlet(ViewletBase):
    """ Viewlet that implements the editing interface for the city profile
    """

    def state_labels(self):
        return {
            'private': 'Private',
            'published': 'Published',
            'pending': 'Pending aproval',
        }

    def render(self):
        print "WC: ", get_working_copy(self.context)
        print "Baseline: ", get_baseline(self.context)

        if not self.available():
            return ""
        return super(EditMenuViewlet, self).render()

    def available(self):
        return is_citymayor_visitor(self.request)

    def current_state(self):
        return get_state(self.context)

    def can_submit_for_publication(self):
        # TODO: return True if transition submit is available
        return self.current_state() == 'private'

    def has_working_copy(self):
        return get_working_copy(self.context) is not None


class ExpiredTokenViewlet(ViewletBase):
    """ Viewlet that appears when a user tries to access a city profile
        with an expired token
    """

    def render(self):
        if self.available():
            return ""
        return super(ExpiredTokenViewlet, self).render()

    def available(self):
        # Check token here
        req = getRequest()

        try:
            secret_token = req.SESSION.get(TOKENID)
        except KeyError:
            secret_token = req.cookies.get(TOKENID)

        if not secret_token:
            return True

        try:
            secret = IAnnotations(self.context)['eea.climateadapt.cityprofile_secret']
            tokenlib.parse_token(secret_token, secret=secret)
            return True
        except ExpiredTokenError:
            return False
        except MalformedTokenError:
            return False
        except InvalidSignatureError:
            return False
