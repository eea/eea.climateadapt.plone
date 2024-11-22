""" City profile content
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from datetime import date, timedelta
from plone.api import user
from plone.api.portal import getSite
from plone.directives import dexterity, form
from tokenlib.errors import ExpiredTokenError
from zope.annotation.interfaces import IAnnotations
from zope.globalrequest import getRequest
from zope.interface import Interface, implements
import binascii
import os
import os.path
import tokenlib


TOKEN_COOKIE_NAME = 'cptk'
TOKEN_EXPIRES_KEY = 'eea.climateadapt.cityprofile_token_expires'
TOKEN_KEY = 'eea.climateadapt.cityprofile_token'
SECRET_KEY = 'eea.climateadapt.cityprofile_secret'
TIMEOUT = 2419200    # How long a token link is valid? 28 days default

OK = object()       # markers for check_public_token response
EXPIRED = object()
NOTGOOD = False


class ICityProfile(form.Schema):
    """
    Defines content-type schema for CityProfile
    """


class ICityProfileStaging(Interface):
    """ A marker interface for CityProfiles.

    It is needed because behaviors (such as IStagingBehavior) are applied as
    marker interfaces to the object and such are more concrete when trying to
    lookup a view on CityProfiles. Basically, it is needed to be able to
    reimplement the @@iterate-control as an override view
    """


def generate_secret():
    """ Generates the token secret key """

    return binascii.hexlify(os.urandom(16)).upper()


def check_public_token(context, request):
    """ Check and parse token for exceptions """

    public_token = request.cookies.get(TOKEN_COOKIE_NAME)

    if public_token is None:
        return NOTGOOD

    try:
        secret = IAnnotations(context)[SECRET_KEY]
        tokenlib.parse_token(public_token, secret=secret)
        return OK
    except ExpiredTokenError:
        return EXPIRED
    except Exception:
        return NOTGOOD

    return NOTGOOD


class CityProfile(dexterity.Container):
    implements(ICityProfile)

    search_type = "MAYORSADAPT"
    security = ClassSecurityInfo()

    def __init__(self, *args, **kw):
        super(CityProfile, self).__init__(*args, **kw)
        self._reset_secret_key()

    @property
    def __ac_local_roles__(self):
        if check_public_token(self, getRequest()) == OK:
            return {'CityMayor': ['Owner', ]}
        else:
            return {}

    def _reset_secret_key(self):
        # TODO: create a public method for this, to allow invalidation of links
        IAnnotations(self)[SECRET_KEY] = generate_secret()

    def _get_public_token(self):
        """ When asked for a new public token, it will generate a new public
        key, with a new expiration date
        """

        secret = IAnnotations(self)[SECRET_KEY]
        public = tokenlib.make_token({}, secret=secret, timeout=TIMEOUT)

        expiry_date = date.today() + timedelta(seconds=TIMEOUT)
        IAnnotations(self)[TOKEN_EXPIRES_KEY] = expiry_date
        IAnnotations(self)[TOKEN_KEY] = public

        return public

    security.declarePrivate('get_existing_edit_link')
    def get_existing_edit_link(self):
        site = getSite()
        publictoken = IAnnotations(self).get(TOKEN_KEY, '-missingtoken-')
        url = "{0}/cptk/{1}/{2}".format(site.absolute_url(),
                                        publictoken,
                                        self.getId()
                                        )
        print("Token url: ", url)
        return url

    #security.declareProtected('Modify portal content', 'get_private_edit_link')
    security.declarePrivate('get_private_edit_link')
    def get_private_edit_link(self):
        """ Returns the link to edit a city profile
        """

        site = getSite()
        url = "{0}/cptk/{1}/{2}".format(site.absolute_url(),
                                        self._get_public_token(),
                                        self.getId()
                                        )
        print("Token url: ", url)
        return url

    def can_reset_token(self):
        """ Returns True if current logged in user can reset public token
        """
        roles = set(['Editor', 'Manager'])
        here_roles = set(user.get_roles(obj=self))
        return bool(roles.intersection(here_roles))
