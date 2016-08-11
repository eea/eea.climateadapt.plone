#!/usr/bin/python
# -*- coding: utf-8 -*-

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from Acquisition import aq_inner
from eea.climateadapt.config import CONTACT_MAIL_LIST, REGISTER_MAIL_LIST
from eea.climateadapt.schema import Email
from plone import api
from plone.directives import form
from plone.formwidget.recaptcha.interfaces import IReCaptchaSettings
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget
from Products.Five.browser import BrowserView
from z3c.form import button, field
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Interface, Invalid, implements, invariant


class ISimplifiedResourceRegistriesView(Interface):
    """ A view with simplified resource registries """


class TransRegionView(BrowserView):
    """ Custom view for /transnational-regions """
    implements(ISimplifiedResourceRegistriesView)


class CountriesView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/countries """
    implements(ISimplifiedResourceRegistriesView)


class MapViewerView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/tools/map-viewer """

    implements(ISimplifiedResourceRegistriesView)

    def __call__(self):
        return self.request.response.redirect('/tools/map-viewer?' +
                                              self.request['QUERY_STRING'])


class SatView(BrowserView):
    """ A http://climate-adapt.eea.europa.eu/sat custom view """
    implements(ISimplifiedResourceRegistriesView)


class AdaptationStrategyView (BrowserView):
    """ Redirect for http://climate-adapt.eea.europa.eu/adaptation-strategies
        to /countries-view-map
    """

    def __call__(self):
        return self.request.response.redirect('/countries')


class RedirectToSearchView (BrowserView):
    """ Custom view for /content """

    def __call__(self):
        type_name = self.context.getProperty('search_type_name', '')
        url = '/data-and-downloads'
        if type_name:
            url += '#searchtype=' + type_name

        return self.request.response.redirect(url)


class IContactForm(form.Schema):
    name = schema.TextLine(title=u"Name:", required=True)
    email = Email(title=u"Email:", required=True)
    feedback = schema.Choice(title=u"Type of feedback:", required=True,
                             values=[
                                 "Request for information",
                                 "Suggestion for Improvement",
                                 "Broken link",
                             ])
    message = schema.Text(title=u"Message:", required=True)

    captcha = schema.TextLine(
        title=u"ReCaptcha",
        description=u"",
        required=False
    )


class ContactForm(form.SchemaForm):
    """ Contact Form
    """

    schema = IContactForm
    ignoreContext = True

    label = u"Contact CLIMATE-ADAPT"
    description = u""" Please use the contact form below if you have questions
    on CLIMATE-ADAPT, to suggest improvements for CLIMATE-ADAPT or to report
    broken links.
    """

    fields = field.Fields(IContactForm)
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
            # emailto = str(api.portal.getSite().email_from_address)

            mime_msg = MIMEText(data.get('message'))
            mime_msg['Subject'] = data.get('feedback')
            mime_msg['From'] = data.get('email')
            # mime_msg['To'] = ','.join(b for b in CONTACT_MAIL_LIST)
            # mime_msg['To'] = CONTACT_MAIL_LIST

            for m in CONTACT_MAIL_LIST:
                mime_msg['To'] = m

            self.description = u"Email Sent."
            return mail_host.send(mime_msg.as_string())
        else:
            self.description = u"Please complete the Captcha."


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


class IContactFooterForm(form.Schema):
    name = schema.TextLine(title=u"Name:", required=True)
    email = Email(title=u"Your Email:", required=True)
    subject = schema.TextLine(title=u"Subject", required=True)
    message = schema.Text(title=u"Message:", required=True)

    captcha = schema.TextLine(
        title=u"Captcha",
        description=u"",
        required=False
    )


class ContactFooterForm(form.SchemaForm):
    """ Footer Contact Form
    """

    schema = IContactFooterForm
    ignoreContext = True

    label = u"Contact form"
    description = u""" Climate-ADAPT aims to support Europe in adapting to
    climate change. It is an initiative of the European Commission and helps
    users to access and share data and information on expected climate change
    in Europe. Fill in this form to contact the site owners.
    """

    fields = field.Fields(IContactFooterForm)
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
                    'mail': data.get('email'),
                    'url': self.context.absolute_url()}
            text = """

Climate Adapt Website

You are receiving this mail because %(name)s
%(mail)s
is sending feedback about the site you administer at %(url)s.
"""         % info

            mime_msg = MIMEText(data.get('message') + text)
            mime_msg['Subject'] = data.get('subject')
            mime_msg['From'] = data.get('email')
            mime_msg['To'] = str(api.portal.getSite().email_from_address)

            self.description = u"Email Sent."
            return mail_host.send(mime_msg.as_string())
        else:
            self.description = u"Please complete the Captcha."
