from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.api.content import get_state
from plone.api.content import transition
from plone.app.iterate import PloneMessageFactory as _
from plone.app.iterate.interfaces import CheckoutException
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IWCContainerLocator
from plone.app.stagingbehavior.utils import get_baseline
from plone.app.stagingbehavior.utils import get_working_copy
from zope.component import getMultiAdapter, getAdapters


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
        return self.context

    def handle_submit(self):
        transition(self.context, to_state='pending')
        url = '{0}/'.format(self.context.absolute_url())
        return self.request.response.redirect(url)

    def _containers(self):
        """Get a list of potential containers"""
        # NOTE: this code is copied from plone.app.iterate.browser.checkout
        context = aq_inner(self.context)
        for name, locator in getAdapters((context,), IWCContainerLocator):
            if locator.available:
                yield dict(name=name, locator=locator)

    def _checkout(self):
        # NOTE: this code is copied from plone.app.iterate.browser.checkout
        context = aq_inner(self.context)

        containers = list(self._containers())
        location = containers[0]['name']

        # We want to redirect to a specific template, else we might
        # end up downloading a file
        control = getMultiAdapter((context, self.request), name=u"iterate_control")
        if not control.checkout_allowed():
            raise CheckoutException(u"Not allowed")

        locator = None
        try:
            locator = [c['locator']
                       for c in containers if c['name'] == location][0]
        except IndexError:
            IStatusMessage(self.request).addStatusMessage(_("Cannot find checkout location"), type='stop')
            view_url = context.restrictedTraverse("@@plone_context_state").view_url()
            self.request.response.redirect(view_url)
            return

        policy = ICheckinCheckoutPolicy(context)
        wc = policy.checkout(locator())

        # we do this for metadata update side affects which will update lock info
        context.reindexObject('review_state')

        IStatusMessage(self.request).addStatusMessage(_("Check-out created"), type='info')
        #view_url = wc.restrictedTraverse("@@plone_context_state").view_url()
        return wc

    def handle_edit(self):
        obj = get_working_copy(self.context)

        # TODO: use the stagingbehavior API to get the best object, in all cases
        print "WC: ", obj
        print "Baseline: ", get_baseline(self.context)

        if obj is None:
            obj = self.context

        state = get_state(obj)

        if state == 'private':
            url = '{0}/edit'.format(obj.absolute_url())
            return self.request.response.redirect(url)

        elif state == 'published':
            # create copy, go to it
            wc = self._checkout()
            url = '{0}/edit'.format(wc.absolute_url())
            return self.request.response.redirect(url)

        elif state == 'pending':
            # create copy, go to it
            transition(obj, to_state='private')
            url = '{0}/edit'.format(obj.absolute_url())
            return self.request.response.redirect(url)

        raise ValueError ('unknown state')

