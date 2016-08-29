# coding=utf-8

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from eea.climateadapt.config import REGISTER_MAIL_LIST
from eea.climateadapt.mayorsadapt.vocabulary import _climateimpacts
from eea.climateadapt.mayorsadapt.vocabulary import _sectors
from eea.climateadapt.mayorsadapt.vocabulary import _stage_implementation_cycle
from eea.climateadapt.schema import Email
from eea.climateadapt.vocabulary import ace_countries
from email.MIMEText import MIMEText
from plone import api
from plone.directives import form
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget
from z3c.form import button, field
from zope import schema
from zope.component import getMultiAdapter
import json


class IRegisterCityForm(form.Schema):
    name = schema.TextLine(title=u"City Name", required=True)
    email = Email(title=u"Contact eMail:", required=True)

    captcha = schema.TextLine(
        title=u"Captcha",
        description=u"",
        required=False
    )


class RegisterCityForm(form.SchemaForm):
    """ Mayors adapt register city form
    """

    schema = IRegisterCityForm
    ignoreContext = True

    label = u"City Profile"
    description = u""" If you are a city representative currently signing up
    to the Mayors Adapt initiative, please submit the form below and we will
    set up a city profile fact sheet site for you to showcase your city’s work
    on Climate-ADAPT.For any questions please do not hesitate to get in touch
    with our helpdesk at helpdesk@mayors-adapt.eu.
    """

    fields = field.Fields(IRegisterCityForm)
    fields['captcha'].widgetFactory = ReCaptchaFieldWidget

    @button.buttonAndHandler(u"Submit")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        captcha = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='recaptcha'
        )
        if captcha.verify():
            mail_host = api.portal.get_tool(name='MailHost')

            info = {'name': data.get('name'),
                    'email': data.get('email')}

            body_plain = """
There is a new city profile request.

Contact Email:
%(email)s

City Name:
%(name)s
""" % info

            mime_msg = MIMEText(body_plain)
            mime_msg['Subject'] = "City Profile Request"
            mime_msg['From'] = "no-reply@eea.europa.eu"
            for m in REGISTER_MAIL_LIST:
                mime_msg['To'] = m

            self.description = u"Your city profile register request was sent."

            return mail_host.send(mime_msg.as_string())
        else:
            self.description = u"Please complete the Captcha."


class MayorsAdaptPage(BrowserView):
    """ Custom page for http://climate-adapt.eea.europa.eu/mayors-adapt """
    # TODO: remove this page


# TODO: make the following 4 classes a single class

class B_M_Climate_Impacts(BrowserView):
    def __call__(self):
        return json.dumps(_climateimpacts)


class A_M_Country(BrowserView):
    def __call__(self):
        return json.dumps(ace_countries)


class B_M_Sector(BrowserView):
    def __call__(self):
        return json.dumps(_sectors)


class C_M_Stage_Of_The_Implementation_Cycle(BrowserView):
    def __call__(self):
        return json.dumps(_stage_implementation_cycle)


class CitiesListingJson(BrowserView):
    """ json query page used by city profiles map on Mayors Adapt page
    """

    def __call__(self):
        cat = self.context.portal_catalog
        q = {
            'portal_type': 'eea.climateadapt.city_profile'
        }
        for k, v in self.request.form.items():
            v = v and v.strip() or None
            if v:
                q[k] = v
        brains = cat.searchResults(**q)
        res = {}

        for brain in brains:
            res[brain.Title] = brain.getURL()

        return json.dumps(res)
