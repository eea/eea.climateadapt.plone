import os
import os.path
import time
from datetime import date, timedelta
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import tokenlib
from tokenlib.errors import ExpiredTokenError

from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.annotation.interfaces import IAnnotations as ann
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest


curdir = os.path.dirname(__file__)
tpl_path = os.path.join(curdir, "pt/mail_token_expired.txt")
with open(tpl_path) as f:
    mail_text_template = f.read()

tpl_path = os.path.join(curdir, "pt/mail_token_reminder.txt")
with open(tpl_path) as f:
    reminder_text_template = f.read()


class TokenCheckView(BrowserView):
    mail_expired_tpl = ViewPageTemplateFile('pt/mail_token_expired.pt')
    mail_reminder_tpl = ViewPageTemplateFile('pt/mail_token_reminder.pt')

    def send_email(self, html_msg, text_msg, city):
        mail_host = api.portal.get_tool(name='MailHost')

        body_html = html_msg
        body_plain = text_msg

        emailto = city.official_email
        email_subject = 'Expired token email'
        emailfrom = str(api.portal.getSite().email_from_address)

        if not (emailto and emailfrom):
            return

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

        mail_host.send(mime_msg.as_string())

    def __call__(self):
        brains = catalog_search(self)

        for city in brains:
            city = city.getObject()

            if has_token(city):
                diff = time_difference(city)

                if diff == 7:
                    """ Send mail informing he has 1 week left
                    """
                    html_msg = self.mail_reminder_tpl(
                        {'receiver': city.name_and_surname_of_contact_person,
                         'title': city.Title})
                    text_msg = reminder_text_template % \
                        ({'receiver': city.name_and_surname_of_contact_person,
                          'title': city.title})
                    self.send_email(html_msg, text_msg, city)

                if diff == 0:
                    """ Send mail saying that the period expired to mayor
                        and administrator
                    """
                    html_msg = self.mail_expired_tpl(
                        {'receiver': city.name_and_surname_of_contact_person,
                         'title': city.Title})
                    text_msg = mail_text_template % \
                        ({'receiver': city.name_and_surname_of_contact_person,
                          'title': city.title})
                    self.send_email(html_msg, text_msg, city)
            else:
                pass

        return self.index()


def catalog_search(self):
    cat = self.context.portal_catalog

    q = {
        'portal_type': 'eea.climateadapt.city_profile'
    }

    brains = cat.searchResults(**q)

    return brains


def has_token(city):
    if ann(city).get('eea.climateadapt.cityprofile_token_expires'):
        return True
    else:
        return False


def time_difference(city):
    time_left = get_time_left(city)
    time_now = date.today()

    time_delta = (time_left - time_now).days

    return time_delta


def get_time_left(city):
    time_left = ann(city).get('eea.climateadapt.cityprofile_token_expires')

    return time_left
