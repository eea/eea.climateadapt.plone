from eea.climateadapt.city_profile import TOKENID
from eea.climateadapt.mayorsadapt.roleplugin import is_citymayor_visitor
from plone.api.content import get_state
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.layout.viewlets import ViewletBase
from tokenlib.errors import ExpiredTokenError
from tokenlib.errors import InvalidSignatureError
from tokenlib.errors import MalformedTokenError
from zope.annotation.interfaces import IAnnotations
from zope.globalrequest import getRequest
import tokenlib


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
        # print "WC: ", get_working_copy(self.context)
        # print "Baseline: ", get_baseline(self.context)

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

    def get_working_copy(self):

        context = self.context
        policy = ICheckinCheckoutPolicy(context, None)

        if policy is None:
            return False

        wc = policy.getWorkingCopy()
        return wc

    def has_working_copy(self):
        wc = self.get_working_copy()
        if wc is not None:
            return True
        return False


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
        self.check_url = False
        self.expire_value = False
        self.malformed_value = False
        self.invalid_value = False

        req = getRequest()

        try:
            secret_token = req.SESSION.get(TOKENID)
        except KeyError:
            secret_token = req.cookies.get(TOKENID)

        if not secret_token:
            self.check_url = False
            return True

        if self.request.getURL().find('cptk') == -1:
            self.check_url = False
            return True

        try:
            ann = IAnnotations(self.context)
            secret = ann['eea.climateadapt.cityprofile_secret']
            tokenlib.parse_token(secret_token, secret=secret)
            self.check_url = True
            self.expire_value = False
            self.malformed_value = False
            self.invalid_value = False
            return True
        except ExpiredTokenError:
            self.expire_value = True
            return False
        except MalformedTokenError:
            self.malformed_value = True
            return False
        except InvalidSignatureError:
            self.invalid_value = True
            return False
