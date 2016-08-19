""" Admin views for city profiles
"""

from AccessControl.unauthorized import Unauthorized
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser import BrowserView
from datetime import date
from eea.climateadapt.city_profile import TOKEN_EXPIRES_KEY
from eea.climateadapt.mayorsadapt.token_email import send_expired_email
from eea.climateadapt.mayorsadapt.token_email import send_newtoken_email
from eea.climateadapt.mayorsadapt.token_email import send_remainder_email
from plone.api import user
from plone.api.content import get_state
from plone.api.portal import show_message
from zope.annotation.interfaces import IAnnotations


class CityAdminView (BrowserView):
    """ Administration of city-profiles. Allow mass sending of token emails

    ATTENTION: This resets tokens on all cities!
    """

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        if 'submit' in self.request.form:
            counter = 0
            for cityid in self.request.form['city']:
                for b in catalog.searchResults(id=[cityid.lower()]):
                    city = b.getObject()
                    city._reset_secret_key()
                    send_newtoken_email(city)
                    counter += 1

            show_message("{0} Email(s) sent".format(counter),
                         request=self.request, type='info')

        cat = self.context.portal_catalog
        q = { 'portal_type': 'eea.climateadapt.city_profile' }
        self.res = [brain.getObject() for brain in cat.searchResults(**q)]

        return self.index()

    def get_status(self, city):
        try:
            return get_state(city)
        except Exception, e:
            return "Error: %s" % e


class SendTokenEmail(BrowserView):
    """ Form handler to send token email to city mayor
    """

    def __call__(self):
        if not self.request.method == 'POST':
            return

        roles = ['Editor', 'Manager']
        if not set(roles).intersection(set(user.get_roles())):
            raise Unauthorized("You are not allowed to send token email")
        email = self.context.official_email
        if email:
            send_newtoken_email(self.context)
            show_message("Email Sent to {0}".format(email),
                        request=self.request, type="info")
        else:
            show_message("Official email is not set",
                         request=self.request, type="error")

        return self.request.response.redirect(self.context.absolute_url())


class BatchSendReminders(BrowserView):
    """ A view to be called from cron that will send email reminders

    TODO: needs to be refactored into a zoperunner script
    """

    def __call__(self):
        # TODO: don't check all cityprofiles, only checkout copied or
        # non-published
        catalog = getToolByName(self.context, 'portal_catalog')
        search = catalog.searchResults
        for city in search(portal_type='eea.climateadapt.city_profile'):
            city = city.getObject()

            if has_token(city):
                diff = time_difference(city)

                if diff <= 7:
                    """ Send mail informing he has 1 week left
                    """
                    send_remainder_email(city)

                if diff == 0:
                    """ Send mail saying that the period expired to mayor
                        and administrator
                    """
                    send_expired_email(city)
            else:
                pass

        return self.index()


def has_token(city):
    if IAnnotations(city).get(TOKEN_EXPIRES_KEY):
        return True
    else:
        return False


def time_difference(city):
    time_left = IAnnotations(city).get(TOKEN_EXPIRES_KEY)
    time_now = date.today()

    time_delta = (time_left - time_now).days

    return time_delta
