# coding=utf-8

import json
from Acquisition import Implicit
from Products.Five.browser import BrowserView
from eea.climateadapt.mayorsadapt.events import CityProfileRegisterEvent
from eea.climateadapt.mayorsadapt.vocabulary import _climateimpacts
from eea.climateadapt.mayorsadapt.vocabulary import _sectors
from eea.climateadapt.mayorsadapt.vocabulary import _stage_implementation_cycle
from eea.climateadapt.schema import Email
from eea.climateadapt.vocabulary import ace_countries
from plone.api.portal import show_message
from plone.directives import form
from plone.formwidget.captcha.widget import CaptchaFieldWidget
from plone.formwidget.captcha.validator import CaptchaValidator, WrongCaptchaCode
from plone.memoize import view
from z3c.form import button, field, validator
from zope import schema
from zope.event import notify
from plone.z3cform.layout import wrap_form


class Captcha(object):
    subject = ""
    captcha = ""

    def __init__(self, context):
        self.context = context


class IRegisterCityForm(form.Schema):
    name = schema.TextLine(title="City Name", required=True)
    email = Email(title="Contact eMail:", required=True)

    captcha = schema.TextLine(
        title="Captcha",
        description="",
        required=False
    )


class CityProfileRegister(Implicit):
    """ A container to be passed to plone.app.contentrules for register info
    """

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email


class RegisterCityForm(form.SchemaForm):
    """ Mayors adapt register city form
    """

    schema = IRegisterCityForm
    ignoreContext = True

    label = "City Profile"
    description = """ If you are a city representative currently signing up
    to the Mayors Adapt initiative, please submit the form below and we will
    set up a city profile fact sheet site for you to showcase your city’s work
    on Climate-ADAPT. For any questions please do not hesitate to get in touch
    with our helpdesk at helpdesk@mayors-adapt.eu.
    """

    fields = field.Fields(IRegisterCityForm)
    fields['captcha'].widgetFactory = CaptchaFieldWidget

    @button.buttonAndHandler("Submit")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        msg = """Registration process completed. You will receive an email
message with details on how to proceed further."""

        if 'captcha' in data:
            # Verify the user input against the captcha
            captcha = CaptchaValidator(self.context, self.request, None, IRegisterCityForm['captcha'], None)

            try:
                valid = captcha.validate(data['captcha'])
            except WrongCaptchaCode:
                show_message(message="Invalid Captcha.",
                             request=self.request, type='error')
                return

            if valid:
                name = data.get('name')
                email = data.get('email')

                obj = CityProfileRegister(name=name, email=email)
                obj = obj.__of__(self.context)
                notify(CityProfileRegisterEvent(obj))
                show_message(message=msg, request=self.request, type='info')
            else:
                show_message(message="Please complete the Captcha.",
                             request=self.request, type='error')


CaptchaForm = wrap_form(RegisterCityForm)

# Register Captcha validator for the captcha field in the IRegisterCityForm
validator.WidgetValidatorDiscriminators(CaptchaValidator, field=IRegisterCityForm['captcha'])


class MayorsAdaptPage(BrowserView):
    """ Custom page for http://climate-adapt.eea.europa.eu/mayors-adapt """
    def __call__(self):
        request = self.context.REQUEST
        url = self.context.absolute_url()
        if url.find('eu-adaptation-policy') == -1:
            request.response.redirect('/eu-adaptation-policy/covenant-of-mayors')
        else:
            return self.index()


# TODO: make the following 4 classes a single class

class B_M_Climate_Impacts(BrowserView):
    @view.memoize
    def __call__(self):
        return json.dumps(_climateimpacts)


class A_M_Country(BrowserView):
    @view.memoize
    def __call__(self):
        return json.dumps(ace_countries)


class B_M_Sector(BrowserView):
    @view.memoize
    def __call__(self):
        return json.dumps(_sectors)


class C_M_Stage_Of_The_Implementation_Cycle(BrowserView):
    @view.memoize
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
        for k, v in list(self.request.form.items()):
            v = v and v.strip() or None
            if v:
                q[k] = v
        brains = cat.searchResults(**q)
        res = {}

        for brain in brains:
            res[brain.Title] = brain.getURL()

        return json.dumps(res)
