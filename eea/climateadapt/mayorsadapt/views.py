from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.api.content import get_state
from plone.api.content import transition
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.iterate import PloneMessageFactory as _
from plone.app.iterate.interfaces import CheckoutException
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserPage


class CityProfileEditController(BrowserView):
    """ Controler script to facilitate Edit action by the City Mayors
    """

    def __call__(self):
        # * if CityProfile is private, go directly to edit page
        # * if CityProfile is pending publication, retract CityProfile to private
        #   state and go do Edit page
        # * if CityProfile is public, make a checkout and go to Edit page on
        #   checkout copy

        action = self.request.form.get('submit')
        if not action:
            return
        else:
            handler = getattr(self, 'handle_' + action)
            return handler()

    def _get_working_copy(self):
        # needed to function as override. TODO: check this statement
        policy = ICheckinCheckoutPolicy(self.context)
        obj = policy.getWorkingCopy()
        return obj

    def handle_submit(self):
        transition(self.context, to_state='pending')
        url = '{0}/'.format(self.context.absolute_url())
        return self.request.response.redirect(url)

    def handle_preview_working_copy(self):
        wc = self._get_working_copy()
        if wc is not None:
            return self.request.response.redirect(wc.absolute_url())
        else:
            return self.request.response.redirect(self.context.absolute_url())

    def handle_check(self):
        policy = ICheckinCheckoutPolicy(self.context)
        baseline = policy.getBaseline()
        if baseline is None:
            baseline = self.context
        return self.request.response.redirect(baseline.absolute_url())

    def _checkout(self):
        # NOTE: this code is copied from plone.app.iterate.browser.checkout
        context = aq_inner(self.context)

        # containers = list(self._containers())
        location = self.context.aq_parent   #containers[0]['name']

        # We want to redirect to a specific template, else we might
        # end up downloading a file
        control = getMultiAdapter((context, self.request),
                                  name="iterate_control")
        if not control.checkout_allowed():
            raise CheckoutException("Not allowed")

        policy = ICheckinCheckoutPolicy(context)
        wc = policy.checkout(location)
        transition(wc, to_state='sent')

        # we do this for metadata update side affects which will update lock info
        context.reindexObject('review_state')

        IStatusMessage(self.request).addStatusMessage(_("Check-out created"),
                                                      type='info')
        #view_url = wc.restrictedTraverse("@@plone_context_state").view_url()
        return wc

    def handle_edit(self):
        policy = ICheckinCheckoutPolicy(self.context)
        obj = policy.getWorkingCopy()

        #baseline = policy.getBaseline()

        if obj is None:
            obj = self.context

        state = get_state(obj)

        if state in ['private', 'sent']:
            url = '{0}/edit'.format(obj.absolute_url())
            return self.request.response.redirect(url)

        elif state == 'published':
            # create copy, go to it
            wc = self._checkout()
            url = '{0}/edit'.format(wc.absolute_url())
            return self.request.response.redirect(url)

        elif state == 'pending':
            # retract object, go to it
            transition(obj, to_state='sent')
            url = '{0}/edit'.format(obj.absolute_url())
            return self.request.response.redirect(url)

        raise ValueError ('unknown state')


class CityRedirector(BrowserPage):
    """ A traverser view registered /-/ that redirects to the
    new /city-profile/ folder
    """

    def publishTraverse(self, request, name):
        city = self.context['city-profile'][name]
        return request.response.redirect(city.absolute_url())


class CitiesProfilesView(FolderView):
    """ Custom view for city-profiles"""
