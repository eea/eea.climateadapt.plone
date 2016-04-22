import binascii
import os
import os.path
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import tokenlib
from tokenlib.errors import (ExpiredTokenError, InvalidSignatureError,
                             MalformedTokenError)
from plone import api
from plone.directives import dexterity, form
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import Interface, implements


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


class ITokenMailView(Interface):
    """Token mail interface"""


class TokenMailView (BrowserView):
    implements(ITokenMailView)

    def __call__(self):
        city = self.context
        tokensecret = IAnnotations(city)['eea.climateadapt.cityprofile_secret']

        # 4 weeks = 2419200
        self.secret = tokenlib.make_token({"": ""}, secret=tokensecret, timeout=2419200)
        self.emailto = str(city.official_email)
        self.receivername = city.name_and_surname_of_contact_person
        self.cityurl = city.virtual_url_path().encode(encoding='UTF-8')

        return self.index()


def generate_secret():
    """ Generates the token secret key """
    return binascii.hexlify(os.urandom(16)).upper()

# The urls look like  /cptk/<token>/city-profile/somecity
TOKENID = 'cptk'

curdir = os.path.dirname(__file__)
tpl_path = os.path.join(curdir, "mayorsadapt/pt/mail_token.txt")

with open(tpl_path) as f:
    MAIL_TEXT_TEMPLATE = f.read()


def send_token_mail(city):
    """ Sends a multipart email that contains the link with token """
    return

    mail_host = api.portal.get_tool(name='MailHost')
    request = getRequest()
    renderer = getMultiAdapter((city, request), name='token_mail')
    html = renderer()

    city_url = city.portal_url() + '/cptk/' + renderer.secret + '/' + renderer.cityurl
    text_plain_dictionary = {'receivername': city.name_and_surname_of_contact_person,
                             'cityurl':  city_url}

    body_plain = MAIL_TEXT_TEMPLATE % (text_plain_dictionary)
    body_html = html
    emailto = str(city.official_email)
    email_subject = 'New token email'
    emailfrom = str(api.portal.getSite().email_from_address)

    mime_msg = MIMEMultipart('related')
    mime_msg['Subject'] = email_subject
    mime_msg['From'] = emailfrom
    mime_msg['To'] = emailto
    mime_msg.preamble = 'This is a multi-part message in MIME format.'

    msgAlternative = MIMEMultipart('alternative')
    mime_msg.attach(msgAlternative)

    # Attach plain text
    msg_txt = MIMEText(body_plain,  _charset='utf-8')
    msgAlternative.attach(msg_txt)

    # Attach html
    msg_txt = MIMEText(body_html, _subtype='html', _charset='utf-8')
    msgAlternative.attach(msg_txt)

    return
    #return mail_host.send(mime_msg.as_string())


def handle_city_added(city, event):
    """ Event handler for when a new city is added """
    send_token_mail(city)


class CityProfile(dexterity.Container):
    implements(ICityProfile)

    search_type = "MAYORSADAPT"

    def __init__(self, *args, **kw):
        super(CityProfile, self).__init__(*args, **kw)
        token_secret = generate_secret()
        IAnnotations(self)['eea.climateadapt.cityprofile_secret'] = token_secret

    @property
    def __ac_local_roles__(self):
        req = getRequest()

        try:
            secret_token = req.SESSION.get(TOKENID)
        except KeyError:
            secret_token = req.cookies.get(TOKENID)

        if not secret_token:
            return {}

        # Parses the token to check for errors
        try:
            secret = IAnnotations(self)['eea.climateadapt.cityprofile_secret']
            tokenlib.parse_token(secret_token, secret=secret)
            return {'CityMayor': ['Owner', ]}
        except ExpiredTokenError:
            return {}
        except MalformedTokenError:
            return {}
        except InvalidSignatureError:
            return {}

        return {}
