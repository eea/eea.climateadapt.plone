from plone.directives import dexterity, form
from zope.annotation.interfaces import IAnnotations
from zope.globalrequest import getRequest
from zope.interface import implements, Interface
import os
import binascii
import datetime
from datetime import timedelta


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


def generate_secret_token():
    return binascii.hexlify(os.urandom(16)).upper()


TOKENID = 'cptk'

current_date = datetime.datetime.now()
expire_date = current_date + timedelta(days=14)


class CityProfile(dexterity.Container):
    implements(ICityProfile)

    search_type = "MAYORSADAPT"

    def __init__(self, *args, **kw):
        super(CityProfile, self).__init__(*args, **kw)
        IAnnotations(self)['eea.climateadapt.cityprofile_secret'] = generate_secret_token()

    @property
    def __ac_local_roles__(self):
        req = getRequest()

        try:
            tk = req.SESSION.get(TOKENID)
        except:
            tk = req.cookies.get(TOKENID)
        if tk and (tk == IAnnotations(self)['eea.climateadapt.cityprofile_secret']):
            return {'CityMayor': ['Owner', ]}
        return {}
