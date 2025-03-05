""" Admin views for city profiles
"""

from datetime import date

import transaction
from AccessControl.unauthorized import Unauthorized
from eea.climateadapt.city_profile import TOKEN_EXPIRES_KEY, TOKEN_KEY
from eea.climateadapt.mayorsadapt.events import (ResetTokenEvent,
                                                 TokenAboutToExpireEvent,
                                                 TokenExpiredEvent)
from plone.api.content import get_state
from plone.api.portal import show_message
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.event import notify


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
                    notify(ResetTokenEvent(city))
                    # send_newtoken_email(city)
                    counter += 1

            show_message("{0} Email(s) sent".format(counter),
                         request=self.request, type='info')

            return self.request.response.redirect(self.context.absolute_url())

        cat = self.context.portal_catalog
        q = {'portal_type': 'eea.climateadapt.city_profile'}
        self.res = [brain.getObject() for brain in cat.searchResults(**q)]

        return self.index()

    def get_status(self, city):
        try:
            return get_state(city)
        except Exception as e:
            return "Error: %s" % e


class SendTokenEmail(BrowserView):
    """ Form handler to send token email to city mayor
    """

    def __call__(self):
        if not self.request.method == 'POST':
            return

        if not self.context.can_reset_token():
            raise Unauthorized("You are not allowed to send token email")
        email = self.context.official_email

        if email:
            # send_newtoken_email(self.context)
            notify(ResetTokenEvent(self.context))
            show_message("Email Sent to {0}".format(email),
                         request=self.request, type="info")
        else:
            show_message("Official email is not set",
                         request=self.request, type="error")

        return self.request.response.redirect(self.context.absolute_url())


def _send_reminders(site):
    catalog = getToolByName(site, 'portal_catalog')
    search = catalog.searchResults

    for city in search(portal_type='eea.climateadapt.city_profile',
                       review_state='sent'):
        city = city.getObject()

        if has_token(city):
            diff = time_difference(city)

            workflowTool = getToolByName(city, 'portal_workflow')

            if diff == 7:  # has 1 week left
                notify(TokenAboutToExpireEvent(city))

            if diff == 0:  # token expired
                notify(TokenExpiredEvent(city))
                workflowTool.doActionFor(city, 'submit')
                transaction.commit()

            if diff < 0:
                workflowTool.doActionFor(city, 'submit')
                transaction.commit()


class BatchSendReminders(BrowserView):
    """ Debugging view that will send email reminders
    """

    def __call__(self):
        _send_reminders(self.context)

        return "Done."
        # return self.index()


def has_token(city):
    expires = IAnnotations(city).get(TOKEN_EXPIRES_KEY)
    public = IAnnotations(city).get(TOKEN_KEY, None)

    return bool(expires and public)


def time_difference(city):
    time_left = IAnnotations(city).get(TOKEN_EXPIRES_KEY)
    time_now = date.today()

    time_delta = (time_left - time_now).days

    return time_delta
