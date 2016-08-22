""" City profile content
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from datetime import date, timedelta
from plone.api.portal import getSite
from plone.directives import dexterity, form
from tokenlib.errors import ExpiredTokenError
from tokenlib.errors import InvalidSignatureError
from tokenlib.errors import MalformedTokenError
from zope.annotation.interfaces import IAnnotations
from zope.globalrequest import getRequest
from zope.interface import Interface, implements
import binascii
import os
import os.path
import tokenlib


TOKEN_COOKIE_NAME = 'cptk'
TOKEN_EXPIRES_KEY = 'eea.climateadapt.cityprofile_token_expires'
SECRET_KEY = 'eea.climateadapt.cityprofile_secret'
TIMEOUT = 2419200    # How long a token link is valid? 28 days default


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


class CityProfile(dexterity.Container):
    implements(ICityProfile)

    search_type = "MAYORSADAPT"
    security = ClassSecurityInfo()

    def __init__(self, *args, **kw):
        super(CityProfile, self).__init__(*args, **kw)
        self._reset_secret_key()

    @property
    def __ac_local_roles__(self):

        req = getRequest()
        public_token = req.cookies.get(TOKEN_COOKIE_NAME)
        print "token", public_token, req['ACTUAL_URL']

        if not public_token:
            return {}

        # Parses the token to check for errors
        try:
            secret = IAnnotations(self)[SECRET_KEY]
            tokenlib.parse_token(public_token, secret=secret)
            return {'CityMayor': ['Owner', ]}
        except ExpiredTokenError:
            return {}
        except MalformedTokenError:
            return {}
        except InvalidSignatureError:
            return {}

        return {}

    def _reset_secret_key(self):
        IAnnotations(self)[SECRET_KEY] = generate_secret()

    def _get_public_token(self):
        """ When asked for a new public token, it will generate a new public
        key, with a new expiration date
        """

        secret = IAnnotations(self)[SECRET_KEY]
        public = tokenlib.make_token({}, secret=secret, timeout=TIMEOUT)

        time_now = date.today()
        expiry_time = time_now + timedelta(seconds=TIMEOUT)
        IAnnotations(self)[TOKEN_EXPIRES_KEY] = expiry_time

        return public

    security.declareProtected('Modify portal content', 'get_private_edit_link')
    def get_private_edit_link(self):
        """ Returns the link to edit a city profile
        """

        site = getSite()
        url = "{0}/cptk/{1}/{2}".format(site.absolute_url(),
                                         self._get_public_token(),
                                         self.getId()
                                         )
        print url
        return url
