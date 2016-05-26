from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.api.content import get_state
from plone.api.content import transition
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.iterate import PloneMessageFactory as _
from plone.app.iterate.interfaces import CheckoutException
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IWCContainerLocator
from zope.component import getMultiAdapter, getAdapters
from zope.interface import Interface, implements
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
        return self.context

    def handle_submit(self):
        transition(self.context, to_state='pending')
        url = '{0}/'.format(self.context.absolute_url())
        return self.request.response.redirect(url)

    # def _containers(self):
    #     """Get a list of potential containers"""
    #     # NOTE: this code is copied from plone.app.iterate.browser.checkout
    #     #yield self.context.aq_parent
    #     context = aq_inner(self.context)
    #     for name, locator in getAdapters((context,), IWCContainerLocator):
    #         if locator.available:
    #             yield dict(name=name, locator=locator)

    def _checkout(self):
        # NOTE: this code is copied from plone.app.iterate.browser.checkout
        context = aq_inner(self.context)

        # containers = list(self._containers())
        location = self.context.aq_parent   #containers[0]['name']

        # We want to redirect to a specific template, else we might
        # end up downloading a file
        control = getMultiAdapter((context, self.request),
                                  name=u"iterate_control")
        if not control.checkout_allowed():
            raise CheckoutException(u"Not allowed")

        # locator = None
        # try:
        #     locator = [c['locator']
        #                for c in containers if c['name'] == location][0]
        # except IndexError:
        #     IStatusMessage(self.request).addStatusMessage(
        #         _("Cannot find checkout location"), type='stop')
        #     view_url = context.restrictedTraverse(
        #         "@@plone_context_state").view_url()
        #     self.request.response.redirect(view_url)
        #     return

        policy = ICheckinCheckoutPolicy(context)
        wc = policy.checkout(location)

        # we do this for metadata update side affects which will update lock info
        context.reindexObject('review_state')

        IStatusMessage(self.request).addStatusMessage(_("Check-out created"),
                                                      type='info')
        #view_url = wc.restrictedTraverse("@@plone_context_state").view_url()
        return wc

    def handle_edit(self):
        policy = ICheckinCheckoutPolicy(self.context)
        obj = policy.getWorkingCopy()
        baseline = policy.getBaseline()

        print "WC: ", obj
        print "Baseline: ", baseline

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


class CityRedirector(BrowserPage):
    """ A traverser view registered /-/ that redirects to the new /city-profile/ folder
    """

    def publishTraverse(self, request, name):
        city = self.context['city-profile'][name]
        return request.response.redirect(city.absolute_url())


class ICitiesProfilesView(Interface):
    """ City Profiles Interface """


class CitiesProfilesView(FolderView):
    """ Custom view for  city-profiles"""

    implements(ICitiesProfilesView)
