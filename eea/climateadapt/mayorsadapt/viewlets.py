from eea.climateadapt.city_profile import TOKEN_COOKIE_NAME
from plone.api import user
from plone.api.content import get_state
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.layout.viewlets import ViewletBase
from tokenlib.errors import ExpiredTokenError
from zope.annotation.interfaces import IAnnotations
import tokenlib

# from tokenlib.errors import InvalidSignatureError
# from tokenlib.errors import MalformedTokenError
#from zope.globalrequest import getRequest


OK = object()
EXPIRED = object()
NOTGOOD = False


def check_public_token(context, request):
    """ Check and parse token for exceptions """

    public_token = request.cookies.get(TOKEN_COOKIE_NAME)

    if public_token is None:
        return NOTGOOD

    try:
        secret = IAnnotations(context)[TOKEN_COOKIE_NAME]
        tokenlib.parse_token(public_token, secret=secret)
        return OK
    except ExpiredTokenError:
        return EXPIRED
    except Exception:
        return NOTGOOD

    return NOTGOOD


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

        if not check_public_token(self.context, self.request) == OK:
            return ""

        return super(EditMenuViewlet, self).render()

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

    def get_baseline_state(self):
        policy = ICheckinCheckoutPolicy(self.context)
        baseline = policy.getBaseline()
        if baseline is None:
            baseline = self.context

        return get_state(baseline)


class ExpiredTokenViewlet(ViewletBase):
    """ Viewlet that appears when a user tries to access a city profile
        with an expired token
    """

    def render(self):
        if check_public_token(self.context, self.request) is not EXPIRED:
            return ""
        return super(ExpiredTokenViewlet, self).render()


class AdminActionsViewlet(ViewletBase):
    """ A viewlet with actions for managers
    """

    def available(self):
        import pdb; pdb.set_trace()
        roles = ['Editor', 'Manager']
        return bool(set(roles).intersection(set(user.get_roles())))
