""" Utilities to deal with sending CityProfile access tokens by email
"""

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from plone.api import portal
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import os


def read(tpl):
    _curdir = os.path.dirname(__file__)
    path = os.path.join(_curdir, tpl)
    res = ''
    with open(path) as f:
        res = f.read()
    return res


EXPIRED_TEXT = read("pt/mail_token_expired.txt")
EXPIRED_HTML = PageTemplateFile('pt/mail_token_expired.pt')

REMINDER_TEXT = read("pt/mail_token_reminder.txt")
REMINDER_HTML = PageTemplateFile('pt/mail_token_reminder.pt')

NEW_TOKEN_TEXT = read("pt/mail_token.txt")
NEW_TOKEN_HTML = PageTemplateFile('pt/mail_token.pt')

TOKENID = 'cptk'


def send_remainder_email(city):
    """ Send a reminder email that token life is about to expire
    """
    d = {'receiver': city.name_and_surname_of_contact_person,
         'title': city.Title}
    html = REMINDER_HTML(**d)
    text = REMINDER_TEXT % (d)

    subject = "Your time to edit the city profile is soon to expire"
    _send_email(subject, html, text, city)


def send_expired_email(city, request):
    """ Send an email about an expired token
    """

    d = {'receiver': city.name_and_surname_of_contact_person,
         'title': city.Title}
    html = EXPIRED_HTML(**d)
    text = EXPIRED_TEXT % (d)

    subject = 'Expired token email'
    _send_email(subject, html, text, city)


def send_newtoken_email(city):
    """ Send an email with the link to edit the city profile.
    """
    d = {'receiver': city.name_and_surname_of_contact_person,
         'cityurl': city.get_private_edit_link()}
    html = NEW_TOKEN_HTML(**d)
    text = NEW_TOKEN_TEXT % (d)

    subject = "Your link to edit the city profile"
    _send_email(subject, html, text, city)


def _send_email(subject, html, text, city):
    """ Send multipart email with html and text
    """

    site = portal.get()
    mail_host = portal.get_tool(name='MailHost')

    emailto = city.official_email
    emailfrom = str(site.email_from_address)

    if not (emailto and emailfrom):
        return

    mime_msg = MIMEMultipart('related')
    mime_msg['Subject'] = subject
    mime_msg['From'] = emailfrom
    mime_msg['To'] = emailto
    mime_msg.preamble = 'This is a multi-part message in MIME format.'

    msgAlternative = MIMEMultipart('alternative')
    mime_msg.attach(msgAlternative)

    # Attach plain text
    msg_txt = MIMEText(text,  _charset='utf-8')
    msgAlternative.attach(msg_txt)

    # Attach html
    msg_html = MIMEText(html, _subtype='html', _charset='utf-8')
    msgAlternative.attach(msg_html)

    mail_host.send(mime_msg.as_string())
